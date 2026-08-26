"""订单重建模块 — 从 order.csv 和 tradeHistory 重建订单完整生命周期。"""

from __future__ import annotations

import logging

import pandas as pd

from .data_loader import load_orders, load_trade_history, xbt_to_xbt

logger = logging.getLogger(__name__)


def rebuild_orders() -> pd.DataFrame:
    """重建订单生命周期。

    返回 DataFrame，每行一个唯一订单，包含：
    - orderID, symbol, side, ordType, ordStatus
    - price, avgPx, stopPx, orderQty, cumQty
    - timestamp (下单时间), fill_time (最后成交时间)
    - time_in_force, execInst, strategy
    - fill_count: 该订单对应的 fill 笔数
    - fill_qty: 该订单对应的总成交量（从 tradeHistory 聚合）
    - fill_pnl: 该订单对应的已实现 PnL 总和（XBt → XBT）
    - qty_match: cumQty == fill_qty（订单记录与成交流水是否一致）
    """
    orders = load_orders()
    trades = load_trade_history()

    # ── 1. 聚合 orders：每个 orderID 取最后一次状态（最新状态） ──
    # BitMEX order API 在状态变化时会产出新行，取最后一行即为最终状态
    orders_agg = (
        orders.sort_values("timestamp")
        .groupby("orderID", as_index=False)
        .last()
    )

    # ── 2. 从 tradeHistory 聚合每个 orderID 的成交信息 ──
    # 只看 Trade 类型的 execution
    trade_fills = trades.groupby("orderID").agg(
        fill_count=("execID", "count"),
        fill_qty=("lastQty", "sum"),
        fill_cost_xbt=("execCost", "sum"),  # XBt 单位
        fill_comm_xbt=("execComm", "sum"),   # XBt 单位
        fill_pnl_xbt=("realisedPnl", "sum"), # XBt 单位
        fill_first_time=("timestamp", "min"),
        fill_last_time=("timestamp", "max"),
    ).reset_index()

    # XBt → XBT 换算
    trade_fills["fill_cost_xbt"] = xbt_to_xbt(trade_fills["fill_cost_xbt"].astype(float))
    trade_fills["fill_comm_xbt"] = xbt_to_xbt(trade_fills["fill_comm_xbt"].astype(float))
    trade_fills["fill_pnl_xbt"] = xbt_to_xbt(trade_fills["fill_pnl_xbt"].astype(float))

    # ── 3. 合并订单与成交信息 ──
    merged = orders_agg.merge(trade_fills, on="orderID", how="left")

    # 没有 fill 的订单（Canceled/Rejected/New）填充 0
    for col in ["fill_count", "fill_qty", "fill_cost_xbt", "fill_comm_xbt", "fill_pnl_xbt"]:
        merged[col] = merged[col].fillna(0)

    # fill 时间：有成交的取最后成交时间，否则为 NaT
    merged["fill_time"] = merged["fill_last_time"]

    # ── 4. 校验：cumQty 与 fill_qty 是否一致 ──
    # 注意：cumQty 可能为 0（Canceled），fill_qty 也应为 0
    merged["qty_match"] = (
        (merged["cumQty"].astype(float) == merged["fill_qty"]) |
        ((merged["cumQty"].astype(float) == 0) & (merged["fill_qty"] == 0))
    )

    # ── 5. 标记订单属性 ──
    # 是否为止损/止盈订单
    merged["is_stop"] = merged["stopPx"].notna() & (merged["stopPx"] > 0)
    merged["is_close"] = merged["execInst"].str.contains("Close", na=False)
    merged["is_reduce_only"] = merged["execInst"].str.contains("ReduceOnly", na=False)
    merged["is_post_only"] = merged["execInst"].str.contains("Participate", na=False)

    # ── 6. 统计 ──
    total = len(merged)
    filled = (merged["ordStatus"] == "Filled").sum()
    canceled = (merged["ordStatus"] == "Canceled").sum()
    qty_mismatch = (~merged["qty_match"]).sum()

    logger.info(f"订单重建完成: {total} 个唯一订单")
    logger.info(f"  Filled: {filled}, Canceled: {canceled}, 其他: {total - filled - canceled}")
    logger.info(f"  qty_match 一致率: {(merged['qty_match'].sum() / total * 100):.1f}%")
    logger.info(f"  qty 不一致: {qty_mismatch} 笔")

    return merged


def get_filled_orders(orders: pd.DataFrame | None = None) -> pd.DataFrame:
    """返回已成交订单的子集。"""
    if orders is None:
        orders = rebuild_orders()
    return orders[orders["ordStatus"] == "Filled"].copy()


def get_canceled_orders(orders: pd.DataFrame | None = None) -> pd.DataFrame:
    """返回已取消订单的子集。"""
    if orders is None:
        orders = rebuild_orders()
    return orders[orders["ordStatus"] == "Canceled"].copy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    orders = rebuild_orders()
    print(f"\n订单重建结果: {orders.shape}")
    print(f"列: {list(orders.columns)}")

    # 抽查前 10 笔已成交订单
    filled = get_filled_orders(orders)
    print(f"\n已成交订单: {len(filled)} 笔")
    print(filled[["orderID", "symbol", "side", "ordType", "orderQty", "avgPx",
                   "fill_count", "fill_qty", "qty_match"]].head(10).to_string())

    # qty 不一致的样例
    mismatch = orders[~orders["qty_match"]]
    if len(mismatch) > 0:
        print(f"\nqty 不一致样例 (前 5):")
        print(mismatch[["orderID", "symbol", "side", "cumQty", "fill_qty", "ordStatus"]].head(5).to_string())