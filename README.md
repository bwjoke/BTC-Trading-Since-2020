# BTC-Trading-Since-2020

>[English](README.md) | [中文](README.zh-CN.md)

Public, continuously updated BitMEX trading context from a single long-duration account that began on 2020-05-01.

![Cumulative performance](cumulative-performance.png)

## Why this exists

Most public trading content is narrative without ledger truth.

This repository does the opposite: it publishes a long-horizon, continuously updated historical mirror of one real BitMEX account so other people can inspect the actual execution ledger, wallet ledger, terminal snapshots, and reconstruction anchors instead of relying on screenshots, selective anecdotes, or marketing summaries.

The core idea is simple: high-quality context compounds. If a public trading history is durable, inspectable, and continuously updated, it becomes more valuable than one-off commentary.

## Dataset window

- First public event in this dataset: **2020-05-01T01:05:55.004Z**
- Latest public event/snapshot in this build: **2026-04-17T16:18:45.506Z**
- Versioning policy: stable root filenames + daily Git commit/tag (`data-2026-04-17` is the tag format)

## What is included

| File | Source endpoint | Role |
|---|---|---|
| `api-v1-execution-tradeHistory.csv` | `/api/v1/execution/tradeHistory` | primary execution ledger |
| `api-v1-order.csv` | `/api/v1/order` | order intent and lifecycle ledger |
| `api-v1-user-walletHistory.csv` | `/api/v1/user/walletHistory?currency=all` | wallet event ledger across deposits, withdrawals, funding, realised pnl, spot trades, conversions |
| `api-v1-position.snapshot.csv` | `/api/v1/position` | terminal position anchor |
| `api-v1-user-wallet.snapshot-all.csv` | `/api/v1/user/wallet?currency=all` | terminal wallet anchor |
| `api-v1-user-margin.snapshot-all.csv` | `/api/v1/user/margin?currency=all` | terminal margin/equity anchor |
| `api-v1-user-walletSummary.all.csv` | `/api/v1/user/walletSummary?currency=all` | BitMEX-generated summary cross-check |
| `api-v1-instrument.all.csv` | `/api/v1/instrument` | instrument dictionary and contract spec reference |
| `api-v1-wallet-assets.csv` | `/api/v1/wallet/assets` | asset scale and wallet metadata reference |
| `derived-equity-curve.csv` | derived | XBT-equivalent wallet curve across XBT and USDt balances used for the chart |
| `cumulative-performance.png` | derived | README performance figure |
| `manifest.json` | derived | checksums, row counts, time ranges, and build metadata |

## High-level facts from this build

- `api-v1-execution-tradeHistory.csv`: **173,058** rows
- `api-v1-order.csv`: **43,214** rows
- `api-v1-user-walletHistory.csv`: **17,099** rows
- Largest single trading symbol by execution count: **XBTUSD** with **104,504** rows (60.39% of `tradeHistory` rows)
- Chart baseline: **1.83953943 XBT** at **2020-05-01T14:39:40.387Z**
- Total completed deposits in XBT ledger: **1.77199051 XBT**
- Total completed withdrawals in XBT ledger: **66.00180000 XBT**
- Latest adjusted wallet-equivalent wealth (XBT+USDt scope): **96.38685218 XBT** (**52.397274x** vs baseline)
- Latest adjusted marked wealth (XBT+USDt scope): **95.75314961 XBT** (**52.052785x** vs baseline)

## How to read the files

- `tradeHistory` is the main balance-affecting execution ledger.
- `order` explains order intent, status transitions, and lifecycle state.
- `walletHistory` is the wallet-side ledger for deposits, withdrawals, funding, realised PnL, spot trades, conversions, and related events.
- `position` / `wallet` / `margin` snapshots are terminal anchors for reconstructing state at the export time.
- `instrument` and `wallet-assets` are reference dictionaries so downstream users can interpret symbols, scales, settlement currencies, and contract metadata using BitMEX-native semantics.
- `walletSummary` is kept as a cross-check layer, not as the primary historical ledger.

## Privacy policy for the public version

- `account` is removed from every published file where it existed.
- `api-v1-user-walletHistory.csv`: `tx` is removed, `text` is removed, and `address` is redacted only when `transactType` is `Withdrawal` or `Transfer`.
- `api-v1-order.csv`: `text` is removed.
- `api-v1-execution-tradeHistory.csv`: `text` is intentionally kept because it helps explain fills, funding, and settlements.
- `/api/v1/user` profile data and `/api/v1/execution` raw lifecycle noise are not published.

## Derived performance methodology

`derived-equity-curve.csv` is intentionally simple and auditable:

1. It tracks **wallet-equivalent wealth across XBT and USDt balances**.
2. The baseline is the first fully-funded XBT wallet balance after the final completed deposit on the first trading day.
3. After that baseline, **completed withdrawals are added back**, **completed deposits are subtracted**, and internal `Transfer` rows are neutralized.
4. `Conversion` and XBT/USDt `SpotTrade` pairs are treated as **internal wallet swaps**, not losses.
5. USDt balances are converted back into XBT using the latest observed internal XBT/USDT conversion or spot rate in the published wallet ledger.
6. The resulting series is a public-friendly XBT-equivalent wealth curve. It is **not** a full historical mark-to-market NAV across every non-XBT wallet or every asset BitMEX ever credited.

This keeps the methodology auditable from the published files themselves while avoiding false cliffs when the account temporarily rotates between XBT and USDt.

## What is intentionally not in this repo

- Raw API secrets
- `/api/v1/user` profile payloads
- `/api/v1/execution` rows that are only lifecycle noise beyond `tradeHistory`
- login/IP/device/profile data
- chain tx hashes from wallet history

## Update policy

This repository is designed for recurring refreshes.

Each update should:

1. pull the full raw dataset from BitMEX,
2. rebuild the public root with the same filenames and privacy rules,
3. commit the new root,
4. tag the commit as `data-YYYY-MM-DD`.

That gives stable filenames for readers and full daily traceability through Git history.
