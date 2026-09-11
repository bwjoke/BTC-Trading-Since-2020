"""持仓曲线重建模块 — 从 tradeHistory 重建每个合约的净持仓量时间序列。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .data_loader import load_trade_history, load_position_snapshot, load_instruments

logger = logging.getLogger(__name__)


def _get_inverse_symbols(trades: pd.DataFrame) -> set[str]:
    """识别反合约（inverse contract）symbol 集合。"""
    inst = load_instruments()
    # 从 trades 中出现的 symbol 与 instrument 表交叉
    trade_symbols = set(trades["symbol"].unique())
    inverse_symbols = set()
    for sym in trade_symbols:
        row = inst[inst["symbol"] == sym]
        if not row.empty and row.iloc[0].get("isInverse", False):
            inverse_symbols.add(sym)
    return inverse_symbols


def build_position_curve(symbol: str | None = None) -> pd.DataFrame:
    """重建持仓曲线。

    参数:
        symbol: 合约名称。None 表示重建所有合约。

    返回:
        DataFrame 列: timestamp, symbol, side(Buy/Sell), orderID,
                       lastQty(成交量), lastPx(成交价), homeNotional(XBT),
                       foreignNotional(USD), net_position(合约数累积),
                       net_position_xbt(XBT 名义价值), realisedPnl_xbt
    """
    trades = load_trade_history()

    # 过滤特定合约
    if symbol:
        trades = trades[trades["symbol"] == symbol].copy()

    # 确保排序
    trades = trades.sort_values(["symbol", "timestamp", "transactTime"]).reset_index(drop=True)

    # 方向：Buy = +1, Sell = -1
    trades["_dir"] = trades["side"].map({"Buy": 1, "Sell": -1})
    trades["_signed_qty"] = trades["lastQty"] * trades["_dir"]

    # ── 按 symbol 分组，计算累积净持仓 ──
    results = []
    for sym, grp in trades.groupby("symbol", sort=False):
        grp = grp.sort_values(["timestamp", "transactTime"]).reset_index(drop=True)
        grp["net_position"] = grp["_signed_qty"].cumsum()

        # XBT 名义价值：homeNotional 已经是 XBT 价值
        grp["net_position_xbt"] = grp["homeNotional"] * grp["_dir"]
        grp["net_position_xbt"] = grp["net_position_xbt"].cumsum()

        # 已实现 PnL 累积
        grp["realisedPnl_xbt"] = grp["realisedPnl"].astype(float).cumsum() / 1_000_000  # XBt → XBT

        # 当前持仓方向标记
        grp["position_direction"] = grp["net_position"].apply(
            lambda x: "Long" if x > 0 else ("Short" if x < 0 else "Flat")
        )

        results.append(grp)

    if not results:
        logger.warning("没有交易数据")
        return pd.DataFrame()

    curve = pd.concat(results, ignore_index=True)

    # 统计
    symbols = curve["symbol"].unique()
    logger.info(f"持仓曲线重建完成: {len(curve)} 行, {len(symbols)} 个合约")
    for sym in sorted(symbols)[:5]:
        sub = curve[curve["symbol"] == sym]
        final_pos = sub.iloc[-1]["net_position"]
        logger.info(f"  {sym}: 最终持仓 = {final_pos:,.0f} 合约")

    if len(symbols) > 5:
        logger.info(f"  ... 以及其他 {len(symbols) - 5} 个合约")

    return curve


def validate_against_snapshot(curve: pd.DataFrame) -> dict[str, dict]:
    """用 terminal position snapshot 交叉验证最终持仓。"""
    snapshot = load_position_snapshot()
    result = {}

    for _, row in snapshot.iterrows():
        sym = row["symbol"]
        expected_qty = float(row["currentQty"])

        # 从曲线中找该合约的最终持仓
        sym_curve = curve[curve["symbol"] == sym]
        if sym_curve.empty:
            result[sym] = {"expected": expected_qty, "actual": None, "match": False}
            continue

        actual_qty = sym_curve.iloc[-1]["net_position"]
        match = abs(actual_qty - expected_qty) < 1  # 允许 1 合约误差（四舍五入）

        result[sym] = {
            "expected": expected_qty,
            "actual": actual_qty,
            "match": match,
        }
        status = "✓" if match else "✗"
        logger.info(f"  {sym}: 期望 {expected_qty:,.0f}, 实际 {actual_qty:,.0f} {status}")

    return result


def get_position_changes(curve: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """提取某个合约的仓位变化点（开仓、平仓、加仓、减仓）。

    返回 DataFrame 列:
        timestamp, symbol, side, orderID, lastQty, lastPx,
        position_before, position_after, position_delta,
        action (Open/Close/Add/Reduce/Reverse),
        direction (Long/Short)
    """
    sym_curve = curve[curve["symbol"] == symbol].sort_values(
        ["timestamp", "transactTime"]
    ).reset_index(drop=True)

    if sym_curve.empty:
        logger.warning(f"合约 {symbol} 无交易数据")
        return pd.DataFrame()

    sym_curve["position_before"] = sym_curve["net_position"].shift(1).fillna(0)
    sym_curve["position_after"] = sym_curve["net_position"]
    sym_curve["position_delta"] = sym_curve["position_after"] - sym_curve["position_before"]

    # 分类每笔交易的动作
    actions = []
    for _, row in sym_curve.iterrows():
        before = row["position_before"]
        after = row["position_after"]
        delta = row["position_delta"]

        if before == 0 and after > 0:
            action = "LongOpen"
        elif before == 0 and after < 0:
            action = "ShortOpen"
        elif before > 0 and after == 0:
            action = "LongClose"
        elif before < 0 and after == 0:
            action = "ShortClose"
        elif before > 0 and after > 0 and delta > 0:
            action = "LongAdd"
        elif before > 0 and after > 0 and delta < 0:
            action = "LongReduce"
        elif before < 0 and after < 0 and delta < 0:
            action = "ShortAdd"
        elif before < 0 and after < 0 and delta > 0:
            action = "ShortReduce"
        elif before > 0 and after < 0:
            action = "ReverseToShort"  # 多翻空
        elif before < 0 and after > 0:
            action = "ReverseToLong"   # 空翻多
        else:
            action = "Unknown"

        actions.append(action)

    sym_curve["action"] = actions

    # 方向标记（基于 position_before 的方向）
    sym_curve["direction"] = sym_curve["position_before"].apply(
        lambda x: "Long" if x > 0 else ("Short" if x < 0 else "Flat")
    )

    return sym_curve


def get_all_position_changes(curve: pd.DataFrame) -> pd.DataFrame:
    """对所有合约提取仓位变化点。"""
    all_changes = []
    for sym in curve["symbol"].unique():
        changes = get_position_changes(curve, sym)
        if not changes.empty:
            all_changes.append(changes)

    if not all_changes:
        return pd.DataFrame()

    result = pd.concat(all_changes, ignore_index=True)
    logger.info(f"全部仓位变化: {len(result)} 条记录")

    # 动作统计
    action_counts = result["action"].value_counts()
    for action, count in action_counts.items():
        logger.info(f"  {action}: {count}")

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # 构建全部持仓曲线
    curve = build_position_curve()

    # 交叉验证
    print("\n=== 交叉验证：与 position snapshot 对比 ===")
    validation = validate_against_snapshot(curve)

    # 主要合约的持仓变化
    for sym in ["XBTUSD", "ETHUSD"]:
        print(f"\n=== {sym} 持仓变化 (前 10 笔) ===")
        changes = get_position_changes(curve, sym)
        if not changes.empty:
            print(changes[["timestamp", "side", "lastQty", "lastPx", "position_before",
                           "position_after", "action"]].head(10).to_string())