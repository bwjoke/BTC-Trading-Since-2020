"""持仓时间分析模块。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .trade_classifier import classify_all_trades, build_trade_rounds

logger = logging.getLogger(__name__)


def analyze_holding_periods(rounds: pd.DataFrame | None = None) -> pd.DataFrame:
    """分析持仓时间分布。

    返回 DataFrame 列:
        round_id, symbol, direction, open_time, close_time,
        holding_seconds, holding_hours, holding_days,
        is_closed
    """
    if rounds is None:
        classified = classify_all_trades()
        rounds = build_trade_rounds(classified)

    df = rounds.copy()
    df["holding_hours"] = df["holding_duration"].dt.total_seconds() / 3600
    df["holding_days"] = df["holding_hours"] / 24

    # 只看已平仓
    closed = df[df["is_closed"]].copy()

    # 按方向分组统计
    stats = {}
    for direction in ["Long", "Short"]:
        sub = closed[closed["direction"] == direction]
        if len(sub) == 0:
            continue
        stats[direction] = {
            "count": len(sub),
            "mean_hours": sub["holding_hours"].mean(),
            "median_hours": sub["holding_hours"].median(),
            "p10_hours": sub["holding_hours"].quantile(0.10),
            "p25_hours": sub["holding_hours"].quantile(0.25),
            "p75_hours": sub["holding_hours"].quantile(0.75),
            "p90_hours": sub["holding_hours"].quantile(0.90),
            "max_hours": sub["holding_hours"].max(),
            "mean_days": sub["holding_days"].mean(),
            "median_days": sub["holding_days"].median(),
        }

    # 持仓时间分类
    closed["holding_category"] = pd.cut(
        closed["holding_hours"],
        bins=[0, 1, 4, 24, 72, 168, 720, float("inf")],
        labels=["<1h", "1-4h", "4-24h", "1-3d", "3-7d", "1-4w", ">4w"],
    )

    logger.info("=== 持仓时间分析 ===")
    logger.info(f"  已平仓周期: {len(closed)}")
    for direction, s in stats.items():
        logger.info(f"  {direction}: {s['count']} 笔, 中位数 {s['median_hours']:.1f}h, 均值 {s['mean_hours']:.1f}h")

    logger.info(f"  持仓时间分布:")
    for cat in ["<1h", "1-4h", "4-24h", "1-3d", "3-7d", "1-4w", ">4w"]:
        count = (closed["holding_category"] == cat).sum()
        pct = count / len(closed) * 100 if len(closed) > 0 else 0
        logger.info(f"    {cat}: {count} ({pct:.1f}%)")

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = analyze_holding_periods()