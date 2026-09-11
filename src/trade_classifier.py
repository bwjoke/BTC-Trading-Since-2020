"""交易分类模块 — 识别每笔交易的开平方向，构建完整的开平仓周期。"""

from __future__ import annotations

import logging

import pandas as pd
import numpy as np

from .position_curve import build_position_curve, get_all_position_changes

logger = logging.getLogger(__name__)


def classify_all_trades() -> pd.DataFrame:
    """对所有合约的所有交易进行分类。

    返回 DataFrame 列:
        timestamp, symbol, side, orderID, lastQty, lastPx,
        homeNotional, foreignNotional,
        position_before, position_after, position_delta,
        action, direction
    """
    curve = build_position_curve()
    changes = get_all_position_changes(curve)
    logger.info(f"交易分类完成: {len(changes)} 条记录")
    return changes


def build_trade_rounds(changes: pd.DataFrame) -> pd.DataFrame:
    """从分类后的交易中提取完整的开平仓周期（Trade Round）。

    一个 Trade Round 定义为：
    - Long Round: 从 LongOpen 到 LongClose（或数据截止）
    - Short Round: 从 ShortOpen 到 ShortClose（或数据截止）

    返回 DataFrame 列:
        round_id, symbol, direction(Long/Short),
        open_time, close_time,
        open_price(加权平均), close_price(加权平均),
        total_qty(最大持仓), total_pnl_xbt,
        holding_duration, is_closed
    """
    rounds = []
    round_id = 0
    data_end_time = changes["timestamp"].max()

    for symbol in sorted(changes["symbol"].unique()):
        sym_changes = changes[changes["symbol"] == symbol].sort_values(
            ["timestamp", "transactTime"]
        ).reset_index(drop=True)

        if sym_changes.empty:
            continue

        # 逐笔跟踪，寻找开平仓周期
        current_round = None

        for _, row in sym_changes.iterrows():
            action = row["action"]

            # 开仓
            if action == "LongOpen":
                current_round = {
                    "direction": "Long",
                    "open_time": row["timestamp"],
                    "open_trades": [],
                    "close_trades": [],
                    "max_position": row["position_after"],
                    "pnl_xbt": 0.0,
                }
                current_round["open_trades"].append(row)
            elif action == "ShortOpen":
                current_round = {
                    "direction": "Short",
                    "open_time": row["timestamp"],
                    "open_trades": [],
                    "close_trades": [],
                    "max_position": row["position_after"],
                    "pnl_xbt": 0.0,
                }
                current_round["open_trades"].append(row)

            # 加仓
            elif action in ("LongAdd", "ShortAdd"):
                if current_round is not None:
                    current_round["open_trades"].append(row)
                    current_round["max_position"] = max(
                        abs(current_round["max_position"]),
                        abs(row["position_after"])
                    )
                    if current_round["direction"] == "Long":
                        current_round["max_position"] = max(
                            current_round["max_position"], row["position_after"]
                        )
                    else:
                        current_round["max_position"] = min(
                            current_round["max_position"], row["position_after"]
                        )

            # 减仓
            elif action in ("LongReduce", "ShortReduce"):
                if current_round is not None:
                    current_round["close_trades"].append(row)
                    current_round["pnl_xbt"] += float(row.get("realisedPnl", 0) or 0) / 1_000_000

            # 平仓
            elif action == "LongClose":
                if current_round is not None and current_round["direction"] == "Long":
                    current_round["close_trades"].append(row)
                    current_round["pnl_xbt"] += float(row.get("realisedPnl", 0) or 0) / 1_000_000
                    # 结束当前周期
                    round_id += 1
                    _finalize_round(rounds, round_id, symbol, current_round, row["timestamp"], is_closed=True)
                    current_round = None

            elif action == "ShortClose":
                if current_round is not None and current_round["direction"] == "Short":
                    current_round["close_trades"].append(row)
                    current_round["pnl_xbt"] += float(row.get("realisedPnl", 0) or 0) / 1_000_000
                    round_id += 1
                    _finalize_round(rounds, round_id, symbol, current_round, row["timestamp"], is_closed=True)
                    current_round = None

            # 翻仓：先平再开
            elif action == "ReverseToShort":
                if current_round is not None and current_round["direction"] == "Long":
                    current_round["close_trades"].append(row)
                    current_round["pnl_xbt"] += float(row.get("realisedPnl", 0) or 0) / 1_000_000
                    round_id += 1
                    _finalize_round(rounds, round_id, symbol, current_round, row["timestamp"], is_closed=True)
                # 开空
                current_round = {
                    "direction": "Short",
                    "open_time": row["timestamp"],
                    "open_trades": [row],
                    "close_trades": [],
                    "max_position": row["position_after"],
                    "pnl_xbt": 0.0,
                }

            elif action == "ReverseToLong":
                if current_round is not None and current_round["direction"] == "Short":
                    current_round["close_trades"].append(row)
                    current_round["pnl_xbt"] += float(row.get("realisedPnl", 0) or 0) / 1_000_000
                    round_id += 1
                    _finalize_round(rounds, round_id, symbol, current_round, row["timestamp"], is_closed=True)
                # 开多
                current_round = {
                    "direction": "Long",
                    "open_time": row["timestamp"],
                    "open_trades": [row],
                    "close_trades": [],
                    "max_position": row["position_after"],
                    "pnl_xbt": 0.0,
                }

        # 未平仓的周期
        if current_round is not None:
            round_id += 1
            _finalize_round(rounds, round_id, symbol, current_round, data_end_time, is_closed=False)

    result = pd.DataFrame(rounds)
    logger.info(f"开平仓周期构建完成: {len(result)} 个周期")
    logger.info(f"  已平仓: {(result['is_closed'] == True).sum()}")  # noqa: E712
    logger.info(f"  未平仓: {(result['is_closed'] == False).sum()}")  # noqa: E712
    logger.info(f"  Long: {(result['direction'] == 'Long').sum()}")
    logger.info(f"  Short: {(result['direction'] == 'Short').sum()}")

    return result


def _finalize_round(rounds, round_id, symbol, current_round, end_time, is_closed):
    """将一个开平仓周期写入结果列表。"""
    open_trades = current_round["open_trades"]
    close_trades = current_round["close_trades"]

    # 加权平均开仓价
    if open_trades:
        total_qty_open = sum(float(t["lastQty"]) for t in open_trades)
        if total_qty_open > 0:
            open_price = sum(float(t["lastPx"]) * float(t["lastQty"]) for t in open_trades) / total_qty_open
        else:
            open_price = 0
    else:
        open_price = 0
        total_qty_open = 0

    # 加权平均平仓价
    if close_trades:
        total_qty_close = sum(float(t["lastQty"]) for t in close_trades)
        if total_qty_close > 0:
            close_price = sum(float(t["lastPx"]) * float(t["lastQty"]) for t in close_trades) / total_qty_close
        else:
            close_price = 0
    else:
        close_price = None
        total_qty_close = 0

    holding_duration = end_time - current_round["open_time"]

    rounds.append({
        "round_id": round_id,
        "symbol": symbol,
        "direction": current_round["direction"],
        "open_time": current_round["open_time"],
        "close_time": end_time if is_closed else None,
        "open_price": open_price,
        "close_price": close_price,
        "max_position": current_round["max_position"],
        "open_trades_count": len(open_trades),
        "close_trades_count": len(close_trades),
        "pnl_xbt": current_round["pnl_xbt"],
        "holding_duration": holding_duration,
        "is_closed": is_closed,
    })


def compute_trade_statistics(rounds: pd.DataFrame) -> dict:
    """计算交易统计指标。"""
    closed = rounds[rounds["is_closed"] == True].copy()  # noqa: E712

    stats = {}

    # 基本统计
    stats["total_rounds"] = len(rounds)
    stats["closed_rounds"] = len(closed)
    stats["open_rounds"] = len(rounds) - len(closed)

    # 方向统计
    stats["long_rounds"] = (rounds["direction"] == "Long").sum()
    stats["short_rounds"] = (rounds["direction"] == "Short").sum()

    if len(closed) > 0:
        # 胜率
        winners = (closed["pnl_xbt"] > 0).sum()
        stats["win_rate"] = winners / len(closed)

        # 盈亏比
        avg_win = closed.loc[closed["pnl_xbt"] > 0, "pnl_xbt"].mean()
        avg_loss = closed.loc[closed["pnl_xbt"] < 0, "pnl_xbt"].mean()
        stats["avg_win_xbt"] = avg_win
        stats["avg_loss_xbt"] = avg_loss
        stats["profit_factor"] = abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")

        # 总 PnL
        stats["total_pnl_xbt"] = closed["pnl_xbt"].sum()

        # 持仓时间统计
        closed["holding_hours"] = closed["holding_duration"].dt.total_seconds() / 3600
        stats["avg_holding_hours"] = closed["holding_hours"].mean()
        stats["median_holding_hours"] = closed["holding_hours"].median()
        stats["max_holding_hours"] = closed["holding_hours"].max()

    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # 分类所有交易
    classified = classify_all_trades()

    # 构建开平仓周期
    rounds = build_trade_rounds(classified)

    # 统计
    stats = compute_trade_statistics(rounds)
    print("\n=== 交易统计 ===")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.6f}")
        else:
            print(f"  {k}: {v}")

    # 前 10 个周期
    print("\n=== 前 10 个开平仓周期 ===")
    print(rounds[["round_id", "symbol", "direction", "open_time", "close_time",
                   "open_price", "close_price", "max_position", "pnl_xbt",
                   "holding_duration", "is_closed"]].head(10).to_string())