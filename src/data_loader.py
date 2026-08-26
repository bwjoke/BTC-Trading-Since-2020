"""数据加载模块 — 加载所有 CSV，处理 BitMEX 特殊数据类型。"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from .constants import (
    EQUITY_CURVE_CSV,
    INSTRUMENT_CSV,
    MANIFEST_JSON,
    MARGIN_SNAPSHOT_CSV,
    ORDER_CSV,
    POSITION_SNAPSHOT_CSV,
    PROJECT_ROOT,
    TRADE_HISTORY_CSV,
    WALLET_ASSETS_CSV,
    WALLET_HISTORY_CSV,
    WALLET_SNAPSHOT_CSV,
    WALLET_SUMMARY_CSV,
    XBt_TO_XBT,
)

logger = logging.getLogger(__name__)


# ── 单位转换工具 ──────────────────────────────────────────

def xbt_to_xbt(xbt_value: pd.Series | float) -> pd.Series | float:
    """BitMEX 内部 XBt 单位 → XBT。1 XBT = 1,000,000 XBt。"""
    return xbt_value / XBt_TO_XBT


# ── 合约规格缓存 ──────────────────────────────────────────

_instrument_cache: pd.DataFrame | None = None


def load_instruments() -> pd.DataFrame:
    """加载合约规格字典，构建 symbol → 规格的查找表。"""
    global _instrument_cache
    if _instrument_cache is not None:
        return _instrument_cache

    df = pd.read_csv(INSTRUMENT_CSV)
    df["symbol"] = df["symbol"].astype(str)

    # 解析 isInverse 标记：BitMEX 反合约（如 XBTUSD）乘数为负
    df["isInverse"] = df["isInverse"].fillna(False).astype(bool)
    df["isQuanto"] = df["isQuanto"].fillna(False).astype(bool)

    _instrument_cache = df
    logger.info(f"加载合约规格: {len(df)} 行, {df['symbol'].nunique()} 个合约")
    return df


def get_instrument_spec(symbol: str) -> dict:
    """获取单个合约的关键规格参数。"""
    inst = load_instruments()
    row = inst[inst["symbol"] == symbol]
    if row.empty:
        return {}
    r = row.iloc[0]
    return {
        "symbol": r["symbol"],
        "isInverse": bool(r.get("isInverse", False)),
        "isQuanto": bool(r.get("isQuanto", False)),
        "multiplier": r.get("multiplier", 1),
        "settlCurrency": r.get("settlCurrency", ""),
        "underlying": r.get("underlying", ""),
        "lotSize": r.get("lotSize", 1),
    }


# ── 数据加载函数 ──────────────────────────────────────────

def load_trade_history() -> pd.DataFrame:
    """加载成交流水（主数据源）。"""
    logger.info("加载 tradeHistory ...")
    df = pd.read_csv(TRADE_HISTORY_CSV, low_memory=False)

    # 时间戳解析
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["transactTime"] = pd.to_datetime(df["transactTime"], utc=True)

    # 只保留 Trade 类型（排除 Settlement, Funding 等非成交事件）
    # execType 包含: Trade, Funding, Settlement 等
    df_trades = df[df["execType"] == "Trade"].copy()
    logger.info(f"  总行数: {len(df)}, Trade 行数: {len(df_trades)}")

    # XBt → XBT 换算（execCost, execComm, realisedPnl 等字段）
    for col in ["execCost", "execComm", "realisedPnl"]:
        if col in df_trades.columns:
            df_trades[col] = df_trades[col].apply(pd.to_numeric, errors="coerce")

    # 保存原始数据供参考
    return df_trades


def load_orders() -> pd.DataFrame:
    """加载订单数据。"""
    logger.info("加载 orders ...")
    df = pd.read_csv(ORDER_CSV, low_memory=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["transactTime"] = pd.to_datetime(df["transactTime"], utc=True)

    # 数值列转换
    for col in ["orderQty", "cumQty", "leavesQty", "price", "avgPx", "stopPx"]:
        if col in df.columns:
            df[col] = df[col].apply(pd.to_numeric, errors="coerce")

    logger.info(f"  订单行数: {len(df)}")
    return df


def load_wallet_history() -> pd.DataFrame:
    """加载钱包历史（出入金、已实现PnL、资金费率等）。"""
    logger.info("加载 walletHistory ...")
    df = pd.read_csv(WALLET_HISTORY_CSV, low_memory=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["transactTime"] = pd.to_datetime(df["transactTime"], utc=True)

    # 数值列
    for col in ["amount", "fee", "walletBalance", "marginBalance"]:
        if col in df.columns:
            df[col] = df[col].apply(pd.to_numeric, errors="coerce")

    logger.info(f"  钱包历史行数: {len(df)}")
    return df


def load_position_snapshot() -> pd.DataFrame:
    """加载终端持仓锚点。"""
    df = pd.read_csv(POSITION_SNAPSHOT_CSV)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    logger.info(f"  终端持仓: {len(df)} 个仓位")
    return df


def load_wallet_snapshot() -> pd.DataFrame:
    """加载终端钱包锚点。"""
    df = pd.read_csv(WALLET_SNAPSHOT_CSV)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def load_margin_snapshot() -> pd.DataFrame:
    """加载终端保证金锚点。"""
    df = pd.read_csv(MARGIN_SNAPSHOT_CSV)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def load_equity_curve() -> pd.DataFrame:
    """加载已导出的 XBT 等价财富曲线。"""
    df = pd.read_csv(EQUITY_CURVE_CSV)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["transactTime"] = pd.to_datetime(df["transactTime"], utc=True)
    logger.info(f"  财富曲线行数: {len(df)}")
    return df


def load_wallet_assets() -> pd.DataFrame:
    """加载资产精度与钱包元数据。"""
    return pd.read_csv(WALLET_ASSETS_CSV)


def load_wallet_summary() -> pd.DataFrame:
    """加载 BitMEX 生成的钱包摘要（交叉校验用）。"""
    return pd.read_csv(WALLET_SUMMARY_CSV)


# ── 校验函数 ──────────────────────────────────────────────

def validate_row_counts() -> dict[str, bool]:
    """校验各 CSV 文件行数与 manifest.json 是否一致。

    注意：CSV 中某些字段含逗号（如 text 列），导致简单的行计数
    与 manifest 中的 pandas 行数不一致。这里用 pandas 加载后的
    实际行数做对比才是准确的。
    """
    with open(MANIFEST_JSON) as f:
        manifest = json.load(f)

    results = {}
    for file_info in manifest["files"]:
        fname = file_info["file"]
        expected = file_info.get("rows")
        if expected is None:
            # 非 CSV 文件（如 PNG）无 rows 字段，跳过
            continue
        fpath = PROJECT_ROOT / fname
        if not fpath.exists():
            results[fname] = False
            logger.warning(f"  文件不存在: {fname}")
            continue
        # 用 pandas 读取实际行数，避免逗号嵌套导致的行数偏差
        try:
            actual = len(pd.read_csv(fpath, low_memory=False))
            ok = actual == expected
            results[fname] = ok
            status = "✓" if ok else f"✗ (期望 {expected}, 实际 {actual})"
        except Exception as e:
            results[fname] = False
            status = f"✗ 读取失败: {e}"
        logger.info(f"  {fname}: {status}")
    return results


def load_all() -> dict[str, pd.DataFrame]:
    """一站式加载所有数据，返回字典。"""
    logger.info("=" * 60)
    logger.info("开始加载全部数据")
    logger.info("=" * 60)

    data = {
        "trades": load_trade_history(),
        "orders": load_orders(),
        "wallet_history": load_wallet_history(),
        "position_snapshot": load_position_snapshot(),
        "wallet_snapshot": load_wallet_snapshot(),
        "margin_snapshot": load_margin_snapshot(),
        "equity_curve": load_equity_curve(),
        "instruments": load_instruments(),
        "wallet_assets": load_wallet_assets(),
        "wallet_summary": load_wallet_summary(),
    }

    # 校验
    logger.info("校验行数 ...")
    row_check = validate_row_counts()
    all_ok = all(row_check.values())
    if all_ok:
        logger.info("✓ 全部行数校验通过")
    else:
        logger.warning("✗ 部分行数校验失败，请检查数据完整性")

    logger.info("全部数据加载完成")
    return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    data = load_all()
    for name, df in data.items():
        print(f"  {name}: {df.shape}")