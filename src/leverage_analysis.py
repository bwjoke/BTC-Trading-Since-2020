"""杠杆分析模块 — 计算实际杠杆使用时间序列。"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .data_loader import load_equity_curve
from .position_curve import build_position_curve

logger = logging.getLogger(__name__)


def compute_leverage_curve() -> pd.DataFrame:
    """计算杠杆时间序列。

    杠杆 = 持仓名义价值(XBT) / 钱包余额(XBT)

    对于 XBTUSD 反合约：
        名义价值(XBT) = |合约数| / BTC价格
        例：持有 10000 合约，BTC 价格 40000，则名义 = 10000/40000 = 0.25 XBT

    返回 DataFrame 列:
        timestamp, symbol, net_position(合约数), lastPx(BTC价格),
        notional_xbt(名义价值), wallet_balance_xbt, leverage
    """
    # ── 1. 获取持仓曲线 ──
    curve = build_position_curve()

    # ── 2. 获取钱包余额曲线 ──
    equity = load_equity_curve()
    equity["timestamp"] = pd.to_datetime(equity["timestamp"], utc=True)
    wallet_balance = equity[["timestamp", "walletBalanceXBTEquivalent"]].copy()
    wallet_balance.rename(columns={"walletBalanceXBTEquivalent": "wallet_balance_xbt"}, inplace=True)

    # ── 3. 计算 XBTUSD 杠杆 ──
    # XBTUSD 反合约：名义价值(XBT) = |合约数| / BTC价格
    xbtusd = curve[curve["symbol"] == "XBTUSD"].copy()
    xbtusd = xbtusd.sort_values("timestamp").reset_index(drop=True)
    xbtusd["notional_xbt"] = xbtusd["net_position"].abs() / xbtusd["lastPx"]

    # ── 4. 合并钱包余额 ──
    xbtusd["timestamp"] = pd.to_datetime(xbtusd["timestamp"], utc=True)
    merged = pd.merge_asof(
        xbtusd.sort_values("timestamp"),
        wallet_balance.sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
    )

    # ── 5. 计算杠杆 ──
    merged["leverage"] = merged["notional_xbt"] / merged["wallet_balance_xbt"]
    merged["leverage"] = merged["leverage"].replace([np.inf, -np.inf], np.nan)

    # 只看有持仓的数据点（排除 Flat）
    active = merged[merged["net_position"] != 0].copy()
    valid_leverage = active["leverage"].dropna()

    logger.info("=== 杠杆分析 (XBTUSD) ===")
    logger.info(f"  有效杠杆数据点: {len(valid_leverage)}")
    logger.info(f"  平均杠杆: {valid_leverage.mean():.2f}x")
    logger.info(f"  中位数杠杆: {valid_leverage.median():.2f}x")
    logger.info(f"  P10 杠杆: {valid_leverage.quantile(0.10):.2f}x")
    logger.info(f"  P25 杠杆: {valid_leverage.quantile(0.25):.2f}x")
    logger.info(f"  P75 杠杆: {valid_leverage.quantile(0.75):.2f}x")
    logger.info(f"  P90 杠杆: {valid_leverage.quantile(0.90):.2f}x")
    logger.info(f"  最大杠杆: {valid_leverage.max():.2f}x")

    # 杠杆分布
    bins = [0, 1, 2, 5, 10, 20, 50, 100]
    labels = ["0-1x", "1-2x", "2-5x", "5-10x", "10-20x", "20-50x", "50-100x"]
    leverage_cats = pd.cut(valid_leverage, bins=bins, labels=labels)
    leverage_dist = leverage_cats.value_counts().sort_index()
    logger.info(f"  杠杆分布:")
    for cat, count in leverage_dist.items():
        pct = count / len(valid_leverage) * 100
        logger.info(f"    {cat}: {count} ({pct:.1f}%)")

    # 按年份统计平均杠杆
    active["year"] = active["timestamp"].dt.year
    yearly_leverage = active.groupby("year")["leverage"].agg(["mean", "median", "max"])
    logger.info(f"\n  按年份平均杠杆:")
    for year, row in yearly_leverage.iterrows():
        logger.info(f"    {year}: 均值 {row['mean']:.2f}x, 中位数 {row['median']:.2f}x, 最大 {row['max']:.2f}x")

    return merged


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    leverage_df = compute_leverage_curve()