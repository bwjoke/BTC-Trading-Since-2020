"""收益分布分析模块 — 基于 walletHistory 的已实现 PnL 计算每笔平仓收益。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .data_loader import load_wallet_history, xbt_to_xbt
from .trade_classifier import classify_all_trades, build_trade_rounds

logger = logging.getLogger(__name__)


def compute_pnl_from_wallet() -> pd.DataFrame:
    """从 walletHistory 提取所有 RealisedPNL 事件。

    返回 DataFrame 列:
        timestamp, transactTime, transactType, symbol(原address), amount_xbt, walletBalance_xbt, marginBalance_xbt
    """
    wh = load_wallet_history()

    # 过滤 RealisedPNL 事件
    pnl_events = wh[wh["transactType"] == "RealisedPNL"].copy()
    # walletHistory 中合约名在 address 列
    pnl_events.rename(columns={"address": "symbol"}, inplace=True)
    pnl_events["amount_xbt"] = pnl_events["amount"] / 1_000_000  # XBt → XBT
    pnl_events["walletBalance_xbt"] = pnl_events["walletBalance"] / 1_000_000
    pnl_events["marginBalance_xbt"] = pnl_events["marginBalance"] / 1_000_000

    logger.info(f"从 walletHistory 提取 RealisedPNL 事件: {len(pnl_events)} 条")
    logger.info(f"  总已实现 PnL: {pnl_events['amount_xbt'].sum():.6f} XBT")

    return pnl_events


def compute_round_pnl(rounds: pd.DataFrame | None = None,
                       pnl_events: pd.DataFrame | None = None) -> pd.DataFrame:
    """为每个开平仓周期计算已实现 PnL。

    方法：将 walletHistory 中的 RealisedPNL 事件按时间和 symbol
    匹配到对应的开平仓周期。

    返回 rounds DataFrame 增加 pnl_from_wallet 列。
    """
    if rounds is None:
        classified = classify_all_trades()
        rounds = build_trade_rounds(classified)
    if pnl_events is None:
        pnl_events = compute_pnl_from_wallet()

    # 为每个周期，累加期间内的 RealisedPNL
    rounds["pnl_from_wallet"] = 0.0

    for idx, row in rounds.iterrows():
        sym = row["symbol"]
        open_t = row["open_time"]
        close_t = row["close_time"] if row["is_closed"] else pd.Timestamp.now(tz="UTC")

        # 匹配同一合约、同一时间段内的 PnL 事件
        mask = (
            (pnl_events["symbol"] == sym) &
            (pnl_events["timestamp"] >= open_t) &
            (pnl_events["timestamp"] <= close_t)
        )
        matched = pnl_events.loc[mask, "amount_xbt"]
        rounds.at[idx, "pnl_from_wallet"] = matched.sum() if len(matched) > 0 else 0.0

    return rounds


def analyze_pnl_distribution(rounds: pd.DataFrame | None = None) -> dict:
    """分析收益分布统计。"""
    if rounds is None or "pnl_from_wallet" not in rounds.columns:
        classified = classify_all_trades()
        rounds_base = build_trade_rounds(classified)
        pnl_events = compute_pnl_from_wallet()
        rounds = compute_round_pnl(rounds_base, pnl_events)

    closed = rounds[rounds["is_closed"]].copy()

    stats = {}
    for direction in ["Long", "Short"]:
        sub = closed[closed["direction"] == direction]
        if len(sub) == 0:
            continue

        winners = sub[sub["pnl_from_wallet"] > 0]
        losers = sub[sub["pnl_from_wallet"] < 0]
        breakeven = sub[sub["pnl_from_wallet"] == 0]

        s = {
            "count": len(sub),
            "win_count": len(winners),
            "loss_count": len(losers),
            "be_count": len(breakeven),
            "win_rate": len(winners) / len(sub) if len(sub) > 0 else 0,
            "total_pnl": sub["pnl_from_wallet"].sum(),
            "avg_pnl": sub["pnl_from_wallet"].mean(),
            "median_pnl": sub["pnl_from_wallet"].median(),
            "avg_win": winners["pnl_from_wallet"].mean() if len(winners) > 0 else 0,
            "avg_loss": losers["pnl_from_wallet"].mean() if len(losers) > 0 else 0,
            "max_win": winners["pnl_from_wallet"].max() if len(winners) > 0 else 0,
            "max_loss": losers["pnl_from_wallet"].min() if len(losers) > 0 else 0,
            "profit_factor": abs(winners["pnl_from_wallet"].sum() / losers["pnl_from_wallet"].sum())
                if len(losers) > 0 and losers["pnl_from_wallet"].sum() != 0 else float("inf"),
        }
        stats[direction] = s

    # 全部
    winners_all = closed[closed["pnl_from_wallet"] > 0]
    losers_all = closed[closed["pnl_from_wallet"] < 0]
    stats["All"] = {
        "count": len(closed),
        "win_count": len(winners_all),
        "loss_count": len(losers_all),
        "win_rate": len(winners_all) / len(closed) if len(closed) > 0 else 0,
        "total_pnl": closed["pnl_from_wallet"].sum(),
        "avg_pnl": closed["pnl_from_wallet"].mean(),
        "median_pnl": closed["pnl_from_wallet"].median(),
        "avg_win": winners_all["pnl_from_wallet"].mean() if len(winners_all) > 0 else 0,
        "avg_loss": losers_all["pnl_from_wallet"].mean() if len(losers_all) > 0 else 0,
        "profit_factor": abs(winners_all["pnl_from_wallet"].sum() / losers_all["pnl_from_wallet"].sum())
            if len(losers_all) > 0 and losers_all["pnl_from_wallet"].sum() != 0 else float("inf"),
    }

    logger.info("=== 收益分布分析 ===")
    for category, s in stats.items():
        logger.info(f"  {category}:")
        logger.info(f"    笔数: {s['count']}, 胜: {s['win_count']}, 负: {s['loss_count']}")
        logger.info(f"    胜率: {s['win_rate']:.2%}")
        logger.info(f"    总 PnL: {s['total_pnl']:.6f} XBT")
        logger.info(f"    平均 PnL: {s['avg_pnl']:.6f} XBT, 中位数: {s['median_pnl']:.6f} XBT")
        logger.info(f"    盈亏比: {s['profit_factor']:.2f}")

    return stats, rounds


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    stats, rounds = analyze_pnl_distribution()