"""回撤分析模块 — 从财富曲线计算 peak-to-trough drawdown。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .data_loader import load_equity_curve

logger = logging.getLogger(__name__)


def compute_drawdown(equity: pd.DataFrame | None = None) -> pd.DataFrame:
    """计算回撤时间序列。

    参数:
        equity: derived-equity-curve 数据。None 则自动加载。

    返回 DataFrame 列:
        timestamp, adjustedWealthXBT, peak, drawdown_xbt, drawdown_pct,
        is_new_peak, drawdown_duration_hours
    """
    if equity is None:
        equity = load_equity_curve()

    df = equity[["timestamp", "adjustedWealthXBT"]].copy()
    df = df.sort_values("timestamp").reset_index(drop=True)

    # ── 1. 计算 peak 和回撤 ──
    df["peak"] = df["adjustedWealthXBT"].cummax()
    df["drawdown_xbt"] = df["adjustedWealthXBT"] - df["peak"]
    df["drawdown_pct"] = df["drawdown_xbt"] / df["peak"]
    df["is_new_peak"] = df["adjustedWealthXBT"] == df["peak"]

    # ── 2. 计算回撤持续时间 ──
    # 从 peak 到 trough 的时间
    df["drawdown_duration_hours"] = np.nan
    peak_time = None
    for i in range(len(df)):
        if df.iloc[i]["is_new_peak"]:
            peak_time = df.iloc[i]["timestamp"]
        if peak_time is not None:
            hours = (df.iloc[i]["timestamp"] - peak_time).total_seconds() / 3600
            df.iloc[i, df.columns.get_loc("drawdown_duration_hours")] = hours

    # ── 3. 统计 ──
    max_dd_pct = df["drawdown_pct"].min()
    max_dd_xbt = df["drawdown_xbt"].min()
    max_dd_idx = df["drawdown_pct"].idxmin()

    logger.info("=== 回撤分析 ===")
    logger.info(f"  最大回撤: {max_dd_pct:.2%} ({max_dd_xbt:.4f} XBT)")
    logger.info(f"  最大回撤时间: {df.loc[max_dd_idx, 'timestamp']}")
    logger.info(f"  最大回撤持续: {df.loc[max_dd_idx, 'drawdown_duration_hours']:.1f} 小时")

    # ── 4. Top 10 回撤事件 ──
    # 识别独立回撤事件：从 peak 开始到恢复 peak
    drawdown_events = []
    in_drawdown = False
    dd_start = None
    dd_peak = None

    for i in range(len(df)):
        if df.iloc[i]["drawdown_pct"] < 0 and not in_drawdown:
            in_drawdown = True
            dd_start = df.iloc[i]["timestamp"]
            dd_peak = df.iloc[i]["peak"]
        elif df.iloc[i]["is_new_peak"] and in_drawdown:
            in_drawdown = False
            dd_end = df.iloc[i]["timestamp"]
            # 找到这个区间内的最大回撤
            mask = (df["timestamp"] >= dd_start) & (df["timestamp"] <= dd_end)
            sub = df.loc[mask]
            max_dd_in_event = sub["drawdown_pct"].min()
            max_dd_time = sub.loc[sub["drawdown_pct"].idxmin(), "timestamp"]
            recovery_hours = (dd_end - dd_start).total_seconds() / 3600
            drawdown_events.append({
                "start_time": dd_start,
                "trough_time": max_dd_time,
                "end_time": dd_end,
                "peak_xbt": dd_peak,
                "trough_xbt": sub.loc[sub["drawdown_pct"].idxmin(), "adjustedWealthXBT"],
                "max_dd_pct": max_dd_in_event,
                "duration_hours": recovery_hours,
                "recovered": True,
            })

    # 如果当前仍在回撤中
    if in_drawdown:
        mask = (df["timestamp"] >= dd_start)
        sub = df.loc[mask]
        max_dd_in_event = sub["drawdown_pct"].min()
        max_dd_time = sub.loc[sub["drawdown_pct"].idxmin(), "timestamp"]
        drawdown_events.append({
            "start_time": dd_start,
            "trough_time": max_dd_time,
            "end_time": None,
            "peak_xbt": dd_peak,
            "trough_xbt": sub.loc[sub["drawdown_pct"].idxmin(), "adjustedWealthXBT"],
            "max_dd_pct": max_dd_in_event,
            "duration_hours": (df.iloc[-1]["timestamp"] - dd_start).total_seconds() / 3600,
            "recovered": False,
        })

    dd_df = pd.DataFrame(drawdown_events)
    dd_df = dd_df.sort_values("max_dd_pct")

    logger.info(f"  总回撤事件数: {len(dd_df)}")
    logger.info(f"  已恢复: {(dd_df['recovered'] == True).sum()}")  # noqa: E712
    logger.info(f"  未恢复: {(dd_df['recovered'] == False).sum()}")  # noqa: E712

    logger.info(f"\n  Top 10 回撤:")
    top10 = dd_df.head(10)
    for _, row in top10.iterrows():
        logger.info(
            f"    {row['start_time'].strftime('%Y-%m-%d')} → "
            f"低点 {row['trough_time'].strftime('%Y-%m-%d')} "
            f"({row['max_dd_pct']:.2%})"
            f"{'  [未恢复]' if not row['recovered'] else ''}"
        )

    # ── 5. 风险指标 ──
    total_return = (df.iloc[-1]["adjustedWealthXBT"] / df.iloc[0]["adjustedWealthXBT"] - 1)
    years = (df.iloc[-1]["timestamp"] - df.iloc[0]["timestamp"]).total_seconds() / (365.25 * 24 * 3600)
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Calmar Ratio = 年化收益 / 最大回撤
    calmar = abs(annualized_return / max_dd_pct) if max_dd_pct != 0 else float("inf")

    logger.info(f"\n  === 风险指标 ===")
    logger.info(f"  总回报: {total_return:.2%}")
    logger.info(f"  年化收益: {annualized_return:.2%}")
    logger.info(f"  时间跨度: {years:.1f} 年")
    logger.info(f"  最大回撤: {max_dd_pct:.2%}")
    logger.info(f"  Calmar Ratio: {calmar:.2f}")

    return df, dd_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    curve, dd_events = compute_drawdown()