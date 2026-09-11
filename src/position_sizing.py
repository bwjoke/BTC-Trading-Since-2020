"""加仓/减仓行为分析模块。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .trade_classifier import classify_all_trades, build_trade_rounds

logger = logging.getLogger(__name__)


def analyze_position_sizing(changes: pd.DataFrame | None = None) -> dict:
    """分析加仓/减仓行为模式。

    返回:
        stats: 统计摘要字典
        add_events: 加仓事件 DataFrame
        reduce_events: 减仓事件 DataFrame
    """
    if changes is None:
        changes = classify_all_trades()

    # 分离加仓和减仓事件
    add_actions = {"LongAdd", "ShortAdd"}
    reduce_actions = {"LongReduce", "ShortReduce"}

    add_events = changes[changes["action"].isin(add_actions)].copy()
    reduce_events = changes[changes["action"].isin(reduce_actions)].copy()

    # ── 加仓分析 ──
    add_events["position_ratio"] = add_events["lastQty"].abs() / add_events["position_before"].abs().replace(0, 1)
    # 加仓量相对当前持仓的比例

    stats = {}

    # 总体统计
    stats["total_add_events"] = len(add_events)
    stats["total_reduce_events"] = len(reduce_events)

    # 按合约统计（只看主要合约）
    for sym in ["XBTUSD", "ETHUSD"]:
        sym_add = add_events[add_events["symbol"] == sym]
        sym_reduce = reduce_events[reduce_events["symbol"] == sym]
        stats[f"{sym}_add_count"] = len(sym_add)
        stats[f"{sym}_reduce_count"] = len(sym_reduce)
        if len(sym_add) > 0:
            stats[f"{sym}_add_avg_ratio"] = sym_add["position_ratio"].mean()
            stats[f"{sym}_add_median_ratio"] = sym_add["position_ratio"].median()

    # 按方向统计
    for action_type, label in [(add_actions, "add"), (reduce_actions, "reduce")]:
        sub = changes[changes["action"].isin(action_type)]
        long_sub = sub[sub["action"].str.startswith("Long")]
        short_sub = sub[sub["action"].str.startswith("Short")]
        stats[f"{label}_long_count"] = len(long_sub)
        stats[f"{label}_short_count"] = len(short_sub)

    # ── 金字塔/倒金字塔模式识别 ──
    # 对每个开平仓周期，分析加仓次数和加仓量变化
    classified = classify_all_trades() if changes is None else changes
    rounds = build_trade_rounds(classified)

    rounds["add_count"] = rounds["open_trades_count"] - 1  # 初始开仓 + 加仓次数
    rounds["add_ratio"] = rounds["add_count"] / rounds["open_trades_count"]

    pyramid_stats = {
        "avg_adds_per_round": rounds["add_count"].mean(),
        "median_adds_per_round": rounds["add_count"].median(),
        "max_adds_per_round": rounds["add_count"].max(),
        "rounds_with_adds": (rounds["add_count"] > 0).sum(),
        "rounds_no_adds": (rounds["add_count"] == 0).sum(),
        "pct_with_adds": (rounds["add_count"] > 0).mean() * 100,
    }
    stats.update(pyramid_stats)

    logger.info("=== 加仓/减仓行为分析 ===")
    logger.info(f"  加仓事件总数: {stats['total_add_events']}")
    logger.info(f"  减仓事件总数: {stats['total_reduce_events']}")
    logger.info(f"  加仓(Long): {stats.get('add_long_count', 0)}, 加仓(Short): {stats.get('add_short_count', 0)}")
    logger.info(f"  减仓(Long): {stats.get('reduce_long_count', 0)}, 减仓(Short): {stats.get('reduce_short_count', 0)}")
    logger.info(f"  每个周期平均加仓次数: {pyramid_stats['avg_adds_per_round']:.1f}")
    logger.info(f"  含加仓的周期比例: {pyramid_stats['pct_with_adds']:.1f}%")

    return stats, add_events, reduce_events


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    stats, add_evts, reduce_evts = analyze_position_sizing()