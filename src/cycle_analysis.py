"""BTC 市场周期分析模块 — 按宏观周期分段评估交易表现。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .data_loader import load_equity_curve
from .trade_classifier import classify_all_trades, build_trade_rounds
from .pnl_analysis import compute_pnl_from_wallet, compute_round_pnl
from .leverage_analysis import compute_leverage_curve

logger = logging.getLogger(__name__)

# ── BTC 市场周期定义 ──
BTC_CYCLES = {
    "COVID_Recovery": ("2020-05-01", "2020-10-01"),
    "Bull_Run":        ("2020-10-01", "2021-04-01"),
    "Top_Range":       ("2021-04-01", "2021-11-01"),
    "Bear_Market":     ("2021-11-01", "2022-11-01"),
    "Bottom_Recovery": ("2022-11-01", "2023-12-01"),
    "ETF_Bull":        ("2023-12-01", "2024-04-01"),
    "New_Cycle":       ("2024-04-01", "2026-08-01"),
}


def analyze_by_cycle(rounds: pd.DataFrame | None = None,
                    leverage_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """按 BTC 市场周期分段统计交易表现。

    返回 DataFrame 列:
        cycle, start, end, trade_count, long_count, short_count,
        total_pnl, avg_pnl, win_rate, avg_leverage, max_leverage
    """
    if rounds is None:
        classified = classify_all_trades()
        rounds_base = build_trade_rounds(classified)
        pnl_events = compute_pnl_from_wallet()
        rounds = compute_round_pnl(rounds_base, pnl_events)
    elif "pnl_from_wallet" not in rounds.columns:
        # 确保 rounds 包含 PnL 数据
        pnl_events = compute_pnl_from_wallet()
        rounds = compute_round_pnl(rounds, pnl_events)

    if leverage_df is None:
        leverage_df = compute_leverage_curve()

    results = []

    for cycle_name, (start_str, end_str) in BTC_CYCLES.items():
        start = pd.Timestamp(start_str, tz="UTC")
        end = pd.Timestamp(end_str, tz="UTC")

        # 筛选该周期内的已平仓周期
        cycle_rounds = rounds[
            (rounds["open_time"] >= start) &
            (rounds["open_time"] < end) &
            rounds["is_closed"]
        ].copy()

        # 筛选该周期内的杠杆数据
        cycle_leverage = leverage_df[
            (leverage_df["timestamp"] >= start) &
            (leverage_df["timestamp"] < end) &
            (leverage_df["net_position"] != 0)
        ]

        if len(cycle_rounds) == 0:
            results.append({
                "cycle": cycle_name, "start": start_str, "end": end_str,
                "trade_count": 0, "long_count": 0, "short_count": 0,
                "total_pnl": 0, "avg_pnl": 0, "win_rate": 0,
                "avg_leverage": np.nan, "max_leverage": np.nan,
            })
            continue

        winners = (cycle_rounds["pnl_from_wallet"] > 0).sum() if "pnl_from_wallet" in cycle_rounds.columns else 0
        total_pnl = cycle_rounds["pnl_from_wallet"].sum() if "pnl_from_wallet" in cycle_rounds.columns else 0

        result = {
            "cycle": cycle_name,
            "start": start_str,
            "end": end_str,
            "trade_count": len(cycle_rounds),
            "long_count": (cycle_rounds["direction"] == "Long").sum(),
            "short_count": (cycle_rounds["direction"] == "Short").sum(),
            "total_pnl": total_pnl,
            "avg_pnl": cycle_rounds["pnl_from_wallet"].mean() if "pnl_from_wallet" in cycle_rounds.columns else 0,
            "win_rate": winners / len(cycle_rounds) if len(cycle_rounds) > 0 else 0,
            "avg_leverage": cycle_leverage["leverage"].mean() if len(cycle_leverage) > 0 and "leverage" in cycle_leverage.columns else np.nan,
            "max_leverage": cycle_leverage["leverage"].max() if len(cycle_leverage) > 0 and "leverage" in cycle_leverage.columns else np.nan,
        }
        results.append(result)

    df = pd.DataFrame(results)

    logger.info("=== BTC 市场周期分析 ===")
    logger.info(f"{'周期':<12} {'笔数':>5} {'Long':>5} {'Short':>5} {'总PnL(XBT)':>12} {'胜率':>8} {'均杠杆':>8} {'最大杠杆':>8}")
    logger.info("-" * 80)
    for _, row in df.iterrows():
        avg_lev = f"{row['avg_leverage']:.2f}x" if pd.notna(row['avg_leverage']) else "N/A"
        max_lev = f"{row['max_leverage']:.2f}x" if pd.notna(row['max_leverage']) else "N/A"
        logger.info(
            f"{row['cycle']:<12} {row['trade_count']:>5} {row['long_count']:>5} {row['short_count']:>5} "
            f"{row['total_pnl']:>12.4f} {row['win_rate']:>7.1%} {avg_lev:>8} {max_lev:>8}"
        )

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cycle_df = analyze_by_cycle()