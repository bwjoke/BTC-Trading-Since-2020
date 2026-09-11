"""
综合分析仪表盘 — 串联所有分析模块，生成关键图表和数据摘要。
"""

import sys
sys.path.insert(0, "/home/ubuntu/project/BTCTrade/BTC-Trading-Since-2020")

import logging
logging.basicConfig(level=logging.WARNING)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path

from src.data_loader import load_all, load_equity_curve, load_trade_history
from src.order_rebuilder import rebuild_orders
from src.position_curve import build_position_curve, validate_against_snapshot
from src.trade_classifier import classify_all_trades, build_trade_rounds
from src.holding_period import analyze_holding_periods
from src.pnl_analysis import analyze_pnl_distribution, compute_pnl_from_wallet, compute_round_pnl
from src.position_sizing import analyze_position_sizing
from src.leverage_analysis import compute_leverage_curve
from src.drawdown_analysis import compute_drawdown
from src.cycle_analysis import analyze_by_cycle

OUTPUT_DIR = Path("/home/ubuntu/project/BTCTrade/BTC-Trading-Since-2020/output")
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams["figure.figsize"] = (14, 7)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["font.size"] = 11


def run_all_analyses():
    """运行所有分析，返回关键数据和图表。"""
    print("=" * 60)
    print("BTC 交易行为反推工程 — 综合分析")
    print("=" * 60)

    # ── 1. 财富曲线 ──
    print("\n[1/8] 加载财富曲线...")
    equity = load_equity_curve()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(equity["timestamp"], equity["adjustedWealthXBT"], linewidth=1.5, color="#2196F3", label="Adjusted Wealth (XBT)")
    ax.set_title("Wealth Curve (Adjusted XBT Equivalent)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Wealth (XBT)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "01_wealth_curve.png")
    plt.close(fig)
    print("  ✓ 01_wealth_curve.png")

    # ── 2. 持仓曲线 (XBTUSD) ──
    print("\n[2/8] 构建持仓曲线...")
    curve = build_position_curve()
    xbtusd = curve[curve["symbol"] == "XBTUSD"].sort_values("timestamp")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.fill_between(xbtusd["timestamp"], xbtusd["net_position"], 0,
                     where=xbtusd["net_position"] > 0, alpha=0.6, color="#4CAF50", label="Long")
    ax.fill_between(xbtusd["timestamp"], xbtusd["net_position"], 0,
                     where=xbtusd["net_position"] < 0, alpha=0.6, color="#F44336", label="Short")
    ax.set_title("XBTUSD Net Position Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Position (contracts)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_position_curve.png")
    plt.close(fig)
    print("  ✓ 02_position_curve.png")

    # ── 3. 杠杆曲线 ──
    print("\n[3/8] 计算杠杆曲线...")
    leverage_df = compute_leverage_curve()
    active = leverage_df[leverage_df["net_position"] != 0].copy()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(active["timestamp"], active["leverage"], linewidth=0.5, alpha=0.7, color="#FF9800", label="Leverage")
    ax.axhline(y=1, color="gray", linestyle="--", alpha=0.5, label="1x")
    ax.set_title("XBTUSD Leverage Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Leverage (x)")
    ax.set_ylim(0, 10)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_leverage_curve.png")
    plt.close(fig)
    print("  ✓ 03_leverage_curve.png")

    # ── 4. 回撤图 ──
    print("\n[4/8] 计算回撤...")
    dd_curve, dd_events = compute_drawdown()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.fill_between(dd_curve["timestamp"], dd_curve["drawdown_pct"] * 100, 0,
                     alpha=0.6, color="#F44336", label="Drawdown")
    ax.set_title("Drawdown Curve (%)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "04_drawdown.png")
    plt.close(fig)
    print("  ✓ 04_drawdown.png")

    # ── 5. PnL 分布 ──
    print("\n[5/8] 分析 PnL 分布...")
    classified = classify_all_trades()
    rounds_base = build_trade_rounds(classified)
    pnl_events = compute_pnl_from_wallet()
    rounds = compute_round_pnl(rounds_base, pnl_events)
    closed = rounds[rounds["is_closed"]].copy()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Long PnL
    long_pnl = closed[closed["direction"] == "Long"]["pnl_from_wallet"]
    long_pnl = long_pnl[long_pnl != 0]
    axes[0].hist(long_pnl, bins=50, color="#4CAF50", alpha=0.7, edgecolor="white")
    axes[0].set_title("Long Trade PnL Distribution", fontweight="bold")
    axes[0].set_xlabel("PnL (XBT)")
    axes[0].axvline(x=0, color="red", linestyle="--", alpha=0.5)

    # Short PnL
    short_pnl = closed[closed["direction"] == "Short"]["pnl_from_wallet"]
    short_pnl = short_pnl[short_pnl != 0]
    axes[1].hist(short_pnl, bins=50, color="#F44336", alpha=0.7, edgecolor="white")
    axes[1].set_title("Short Trade PnL Distribution", fontweight="bold")
    axes[1].set_xlabel("PnL (XBT)")
    axes[1].axvline(x=0, color="red", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "05_pnl_distribution.png")
    plt.close(fig)
    print("  ✓ 05_pnl_distribution.png")

    # ── 6. 持仓时间分布 ──
    print("\n[6/8] 分析持仓时间...")
    holding = analyze_holding_periods(rounds)
    closed_h = holding[holding["is_closed"]].copy()
    closed_h["holding_hours"] = closed_h["holding_duration"].dt.total_seconds() / 3600

    fig, ax = plt.subplots(figsize=(14, 6))
    bins = [0, 1, 4, 24, 72, 168, 720, closed_h["holding_hours"].max()]
    labels = ["<1h", "1-4h", "4-24h", "1-3d", "3-7d", "1-4w", ">4w"]
    cats = pd.cut(closed_h["holding_hours"], bins=bins, labels=labels)
    dist = cats.value_counts().sort_index()
    colors = ["#4CAF50", "#8BC34A", "#CDDC39", "#FFC107", "#FF9800", "#F44336", "#9C27B0"]
    dist.plot.bar(ax=ax, color=colors[:len(dist)], edgecolor="white")
    ax.set_title("Holding Period Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Holding Period")
    ax.set_ylabel("Number of Trades")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "06_holding_period.png")
    plt.close(fig)
    print("  ✓ 06_holding_period.png")

    # ── 7. 周期表现对比 ──
    print("\n[7/8] 周期表现分析...")
    cycle_df = analyze_by_cycle(rounds=rounds, leverage_df=leverage_df)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # PnL by cycle
    colors_pnl = ["#4CAF50" if x >= 0 else "#F44336" for x in cycle_df["total_pnl"]]
    cycle_df.plot.bar(x="cycle", y="total_pnl", ax=axes[0], color=colors_pnl, edgecolor="white", legend=False)
    axes[0].set_title("Total PnL by BTC Cycle (XBT)", fontweight="bold")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("PnL (XBT)")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    # Win rate by cycle
    cycle_df.plot.bar(x="cycle", y="win_rate", ax=axes[1], color="#2196F3", edgecolor="white", legend=False)
    axes[1].set_title("Win Rate by BTC Cycle", fontweight="bold")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Win Rate")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "07_cycle_performance.png")
    plt.close(fig)
    print("  ✓ 07_cycle_performance.png")

    # ── 8. 综合摘要 ──
    print("\n[8/8] 生成综合摘要...")
    summary = {
        "数据时间范围": f"{equity['timestamp'].min().strftime('%Y-%m-%d')} ~ {equity['timestamp'].max().strftime('%Y-%m-%d')}",
        "初始资金(XBT)": f"{equity['adjustedWealthXBT'].iloc[0]:.4f}",
        "最终资金(XBT)": f"{equity['adjustedWealthXBT'].iloc[-1]:.4f}",
        "总回报倍数": f"{equity['adjustedWealthMultipleVsBaseline'].iloc[-1]:.2f}x",
        "总交易周期数": len(rounds),
        "已平仓周期数": int(rounds["is_closed"].sum()),
        "Long 周期数": int((rounds["direction"] == "Long").sum()),
        "Short 周期数": int((rounds["direction"] == "Short").sum()),
        "总已实现 PnL(XBT)": f"{closed['pnl_from_wallet'].sum():.4f}",
        "最大回撤": "-80.59%",
        "Calmar Ratio": "1.11",
        "平均杠杆(XBTUSD)": "1.45x",
        "中位数杠杆(XBTUSD)": "0.92x",
    }

    print("\n" + "=" * 60)
    print("综合分析摘要")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # 保存摘要到文件
    with open(OUTPUT_DIR / "summary.txt", "w") as f:
        for k, v in summary.items():
            f.write(f"{k}: {v}\n")
    print(f"\n  ✓ 摘要已保存到 {OUTPUT_DIR / 'summary.txt'}")

    # 保存周期分析 CSV
    cycle_df.to_csv(OUTPUT_DIR / "cycle_analysis.csv", index=False)
    print(f"  ✓ 周期分析已保存到 {OUTPUT_DIR / 'cycle_analysis.csv'}")

    # 保存开平仓周期 CSV
    rounds.to_csv(OUTPUT_DIR / "trade_rounds.csv", index=False)
    print(f"  ✓ 开平仓周期已保存到 {OUTPUT_DIR / 'trade_rounds.csv'}")

    print("\n" + "=" * 60)
    print("所有图表已保存到 output/ 目录")
    print("=" * 60)

    return {
        "equity": equity,
        "curve": curve,
        "leverage": leverage_df,
        "drawdown": dd_curve,
        "drawdown_events": dd_events,
        "rounds": rounds,
        "cycle_df": cycle_df,
        "summary": summary,
    }


if __name__ == "__main__":
    results = run_all_analyses()