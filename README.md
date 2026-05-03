# BTC-Trading-Since-2020

>[English](README.md) | [中文](README.zh-CN.md)

In the AI era, high-quality context becomes the most scarce asset.
This repository is an open-intelligence experiment: a public, inspectable, and continuously extensible mirror of a real trading account. It spans nearly six years, 43k+ orders, and 173k+ execution rows.
The internet likely has no comparable public repository that continuously exposes the full multi-year secondary-market history of a predominantly BTC-trading account at this level of detail.

**This archive is more about decision quality under uncertainty than prediction quality over price.**

![Cumulative performance](cumulative-performance.png?v=b642b68b1500)

BitMEX recognized Paul Wei ([`@coolish`](https://x.com/coolish)) as one of its 11th anniversary Legends and, on its public Hall of Legends page, highlighted a `70x` Bitcoin-trading return over 3 years ([source](https://www.bitmex.com/hall-of-legends)). But the deeper value of this repository is not a single headline number. It is a public, timestamped archive of long-term BTC trading through multiple market cycles — including strong calls, reversals, drawdowns, and recoveries — so readers can inspect the record in sequence rather than rely on retrospective storytelling.

Any long-term result includes timing and luck. What makes this archive unusual is that much of the trail was public before the outcome was known. That makes it a more durable record of decision-making under uncertainty, not just a curated victory lap.

## Why this exists

Most public trading content is narrative without ledger truth.

This repository does the opposite: it publishes a long-horizon, continuously updated historical mirror of one real trading account so other people can inspect the actual execution ledger, wallet ledger, terminal snapshots, and reconstruction anchors instead of relying on screenshots, selective anecdotes, or marketing summaries.

Open intelligence instead of selective narrative.

## How to read this dataset

This is **not** a dataset for HFT (**high-frequency trading**), CLOB (**central limit order book**) microstructure work, or millisecond price prediction.
Read it instead as a timestamped archive of manual, discretionary, chart-driven BTC trading: regime adaptation, position sizing, risk management, drawdown handling, and long-term compounding under uncertainty.

## Dataset window

- First public event in this dataset: **2020-05-01T01:05:55.004Z**
- Latest public event/snapshot in this build: **2026-05-03T05:01:51.512Z**
- Versioning policy: stable root filenames + daily Git commit/tag (`data-2026-05-03` is the tag format)

## Download packages

- If you just want a one-click download instead of cloning the full git history, use the GitHub **Releases** page.
- Each tagged build can be attached there as `.zip` and `.tar.gz` archives containing this same flat repo root.

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

- `api-v1-order.csv`: **43,219** rows
- `api-v1-execution-tradeHistory.csv`: **173,113** rows
- `api-v1-user-walletHistory.csv`: **17,177** rows
- Time span: **2020-05-01 → 2026-05-03**
- By executed trade notional, BTC-related symbols account for **~84.0%** of the full archive
- The account becomes much more BTC-concentrated in later years: **~93.7%** from 2022 onward, **~96.1%** from 2023 onward, and **~99.0%** from 2024 onward
- Chart baseline: **1.83953943 XBT** at **2020-05-01T14:39:40.387Z**
- Total completed deposits in XBT ledger: **1.77199051 XBT**
- Total completed withdrawals in XBT ledger: **66.00180000 XBT**
- Latest adjusted wallet-equivalent wealth (XBT+USDt scope): **96.32555393 XBT** (**52.363952x** vs baseline)
- Latest adjusted marked wealth (XBT+USDt scope): **95.20953674 XBT** (**51.757269x** vs baseline)

In plain English: **adjusted wealth** is the wallet-equivalent curve after stripping out later external deposits and adding back later external withdrawals, so it is closer to the trading result itself. **Marked-to-market wealth** uses the same framework but swaps in the current marked margin balance, so it also reflects unrealized PnL still sitting in open positions.

## Reference docs and terminology

- BitMEX API Explorer docs: https://docs.bitmex.com/api-explorer/bitmex-api.html
- BitMEX API Explorer / Swagger JSON: https://www.bitmex.com/api/explorer/swagger.json
- `XBT` is another ticker used by some exchanges for Bitcoin (`BTC`). If you are unfamiliar with the term, see: https://coinmarketcap.com/academy/glossary/xbt

## Live current-state companion

For a real-time dashboard companion to this archive, see: **https://wsnb.online**
This repository is the long-horizon historical layer; `wsnb.online` is the live current-state layer.

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
- `api-v1-execution-tradeHistory.csv`: `text` is intentionally kept because it helps explain fills, funding, and settlements, but non-BitMEX hostnames inside that field are redacted.
- `/api/v1/user` profile data and `/api/v1/execution` raw lifecycle noise are not published.

## Derived performance methodology

`derived-equity-curve.csv` is intentionally simple and auditable:

1. It tracks **wallet-equivalent wealth across XBT and USDt balances**.
2. The baseline is the first fully-funded XBT wallet balance after the final completed deposit on the first trading day.
3. After that baseline, **completed withdrawals are added back**, **completed deposits are subtracted**, and internal `Transfer` rows are neutralized.
4. `Conversion` and XBT/USDt `SpotTrade` pairs are treated as **internal wallet swaps**, not losses.
5. USDt balances are converted back into XBT using the latest observed internal XBT/USDT conversion or spot rate in the published wallet ledger.
6. For wallet-history-driven cash flows, event ordering uses `timestamp` when BitMEX provides it; `transactTime` is preserved as the original exchange field but is not blindly treated as the accounting-effective order.
7. The resulting series is a public-friendly XBT-equivalent wealth curve. It is **not** a full historical mark-to-market NAV across every non-XBT wallet or every asset BitMEX ever credited.

In practice, almost all trading activity in this account was BTC-settled on BitMEX: by executed trade notional grouped by settlement currency, about 98.9% settles in XBT, while only about 1.1% settles in USDt. That is why the realized PnL story is overwhelmingly a story about BTC quantity and BTC-denominated value changing over time; the USDt component is a small supplementary layer; the only completed external deposits were the two initial XBT deposits on 2020-05-01, and there have been no completed deposits since.

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
