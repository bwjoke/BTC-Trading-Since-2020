# BTC-Trading-Since-2020

>[English](README.md) | [中文](README.zh-CN.md)

这是一个 open intelligence 实验：在 AI 时代，高质量上下文会成为最稀缺的资产。
这个仓库把一个真实交易账户自 2020 年 5 月以来的长期历史，做成可公开检查的上下文镜像。本次构建包含 43,258 条订单、173,577 条影响余额的执行记录，以及下文说明的可获取订单生命周期事件。
这种细节等级的多年公开账户账本，让人可以超越截图与事后叙述，直接检查一个以 BTC 交易为主的账户。

**这份档案更关心的是不确定性中的决策质量，而不是对价格的预测质量。**

> **最终归档快照 — 2026-09-11。** 本次是应账户所有者要求进行的最后一次刷新。账户历史账本统一截止到 **2026-09-11T09:43:29Z**；仓位、钱包和保证金快照在其后依次读取，并非同一瞬间的原子快照。各次读取之后的新活动不包含在内。

![累计收益曲线](cumulative-performance.png?v=30f9af45aa64)

BitMEX 在其 11 周年 `Hall of Legends` 页面中，将 Paul Wei（[`@coolish`](https://x.com/coolish)）列为官方传奇交易员之一，并公开强调其“三年内仅比特币交易收益达 70 倍”（[来源](https://www.bitmex.com/zh-hans/hall-of-legends)）。但这个仓库更深一层的价值，不在于某一个 headline 数字，而在于它把一个长期 BTC 交易过程做成了可公开检查、带时间戳、跨越多个市场周期的完整档案。这里面不只有高光，也包括反转、回撤、恢复，以及在不确定性下不断修正判断的全过程。

任何长期结果里都一定会掺杂 timing 和运气。这个档案真正稀缺的地方，是大量痕迹在结果发生之前就已经公开存在，因此别人可以沿着时间顺序去检查，而不是只能接受事后改写过的叙事。

## 为什么要做这件事

大多数公开交易内容，本质上还是叙事，不是账本。

这个仓库反过来：直接公开一个真实交易账户的长期历史镜像，让别人看到真正的成交账本、钱包账本、终态快照和重建锚点，而不是只看截图、只听故事、只读摘要。

Open intelligence，而不是选择性叙事。

## 这份数据更适合怎么读

这**不是**一份给 HFT（**高频交易**）、CLOB（**中央限价订单簿，也就是交易所撮合盘口**）微观结构研究或毫秒级价格预测准备的数据集。
更适合把它当成一份带时间戳的、手工、主观、以看 K 线为主的 BTC 交易档案：看的是在不确定性里如何做仓位、风控、回撤处理、策略应对与长期复利。

## 数据时间范围

- 本次公开数据里的最早事件：**2020-05-01T01:05:55.004Z**
- 账户数据中记录的最新事件/快照时间戳：**2026-07-23T12:56:05.357Z**
- 版本策略：根目录文件名稳定不变，用 Git commit/tag 追踪（`data-YYYY-MM-DD` 按导出日期命名，不按最后一笔事件日期）
- 导出完成时间（UTC）：**2026-09-11T09:57:16Z**。导出时间与账户最后一笔事件时间不是一回事。

## 下载包

- 如果你只是想一键下载，而不是 clone 整个 Git 历史，请优先使用 GitHub 的 **Releases** 页面。
- 每个 tag 版本都可以在那边附带 `.zip` 和 `.tar.gz` 下载包，里面装的是同样这套平铺根目录文件。

## 仓库里包含什么

| File | Source endpoint | Role |
|---|---|---|
| `api-v1-execution.csv` | `/api/v1/execution` | API-returned execution events, including available order lifecycle changes; not a guaranteed complete historical lifecycle log |
| `api-v1-execution-tradeHistory.csv` | `/api/v1/execution/tradeHistory` | primary execution ledger |
| `api-v1-order.csv` | `/api/v1/order` | order intent and latest returned state per order; timestamp-cursor export |
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

## 本次构建的几个关键事实

- `api-v1-execution.csv`：**173,592** 行（本次接口返回的全部 execution 事件）
- `api-v1-order.csv`：**43,258** 行
- `api-v1-execution-tradeHistory.csv`：**173,577** 行
- `api-v1-user-walletHistory.csv`：**17,620** 行
- 时间范围：**2020-05-01 → 2026-07-23**
- 按 executed trade notional 计算，BTC 相关交易约占整份全档案的 **~84.0%**
- 但这个账户在后期明显进一步向 BTC 收敛：若只看 2022 年以来约为 **~93.8%**，2023 年以来约为 **~96.1%**，2024 年以来约为 **~99.0%**
- 曲线基准点：**1.83953943 XBT**，时间 **2020-05-01T14:39:40.387Z**
- XBT 钱包账本里累计完成入金：**1.77199051 XBT**
- XBT 钱包账本里累计完成出金：**99.51625171 XBT**
- 最新调整后钱包等值财富（XBT+USDt 范围）：**99.46454272 XBT**（相对基准 **54.070351x**）
- 最新调整后按保证金计价财富（XBT+USDt 范围）：**n/a — 本次快照未计算该指标**

用更直白的人话说：**adjusted wealth** 可以理解为“把后续外部入金扣掉、把后续外部出金加回之后，更接近纯交易结果的财富曲线”；**marked-to-market wealth** 则是在同样框架下，把当前未平仓头寸的未实现盈亏也按盯市算进去。

## 参考文档与术语说明

- BitMEX API Explorer 文档页：https://docs.bitmex.com/api-explorer/bitmex-api.html
- BitMEX API Explorer / Swagger JSON：https://www.bitmex.com/api/explorer/swagger.json
- `XBT` 是一些交易所对 Bitcoin（`BTC`）使用的另一种 ticker。若你不熟悉这个叫法，可参考：https://coinmarketcap.com/academy/glossary/xbt

## 账号实时状态看板补充

如果你想看社区自发创建的账号实时状态看板（实时仓位与订单数据可视化），可访问：**https://wsnb.online**
这个仓库负责长期历史层；`wsnb.online` 则负责实时状态层。

## 订单导出完整性

本次最终导出改用**时间戳游标分页**，不拆分同一时间戳的订单组，并验证每个 `orderID` 唯一。这修复了早期快照按偏移量分页时，同一时间戳内排序不稳定导致的重复和漏行。因此，订单文件中的部分差异是补回旧记录，不一定是新增交易活动。

## execution 生命周期覆盖范围：使用前请读

本次新增 `api-v1-execution.csv`，公开 [`GET /api/v1/execution`](https://docs.bitmex.com/api-explorer/get-execution) 实际返回的记录。官方描述说明该端点可包含订单创建、撤单、订单状态变化及影响余额的事件；但事件类型的描述不等于对完整历史保留的承诺。

- 本次实际返回的 `execType` 分布：`Funding`: 12,916, `New`: 8, `Replaced`: 6, `Settlement`: 19, `Trade`: 160,642, `TriggeredOrActivatedBySystem`: 1。
- 除 `Trade`、`Funding`、`Settlement` 外的事件：**15** 条；其实际时间范围为 **2025-06-13T00:17:51.654Z → 2025-06-19T21:24:46.794Z**。
- 返回的 `Canceled` 事件：**0** 条；`Rejected` 事件：**0** 条。事件未被返回，不代表对应行为从未发生。
- 这**不代表完整的历史订单生命周期日志**。导出保留 API 返回的内容，不补造缺失的 New/Canceled/Replaced/Rejected 事件，也不从订单快照推算事件发生时间；按日期筛选不能证明历史完整性。
- 用原生 `orderID` 关联 `execution` 与 `order`，用 `execID` 识别单条 execution 事件。`order.csv` 保存接口返回的每个订单状态，不是中间每一步状态迁移日志。建议左连接并**保留无法匹配的 execution 行**：即便 `orderID` 非空，API 也可能未返回对应订单记录。
- 计算盈亏或成交量时，**不要直接拼接** `execution` 和 `tradeHistory`：两者存在重叠。继续用 `tradeHistory` 作为影响余额的执行账本；若组合来源，必须按 `execID` 明确去重。

## 这些文件应该怎么理解

- `execution`：补充接口返回的全部 execution 事件，包括可获取的生命周期变化；覆盖限制见上文。
- `tradeHistory`：主要的、会影响余额的成交执行账本。
- `order`：记录下单意图及接口返回的每个订单最新状态，不是完整状态迁移日志。
- `walletHistory`：钱包侧账本，覆盖入金、出金、资金费、已实现盈亏、现货成交、转换等事件。
- `position` / `wallet` / `margin` 快照：导出时刻的终态锚点，用来帮助重建状态。
- `instrument` 和 `wallet-assets`：参考字典层，用 BitMEX 原生语义解释 symbol、精度、结算货币和合约元数据。
- `walletSummary`：保留为交叉校验层，不作为主历史账本。

## 公版隐私处理规则

- 所有出现过 `account` 的公开文件都删除该列。
- `api-v1-user-walletHistory.csv`：删除 `tx`，删除 `text`，仅在 `transactType` 为 `Withdrawal` 或 `Transfer` 时把 `address` 打成 `Redacted`。
- `api-v1-order.csv`：删除 `text`。
- `api-v1-execution-tradeHistory.csv`：保留 `text`，因为它对解释成交、资金费、结算语义仍有帮助；但该字段中的非 BitMEX 主机名会打成 `Redacted`。
- `api-v1-execution.csv`：保留接口返回的全部事件，但删除 `account`、客户端/经纪商自定义标识（`origClOrdID`、`clOrdID`、`clOrdLinkID`、`brokerLinkID`），以及自由文本或嵌套字段（`text`、`ordRejReason`、`error`、`algoOrderDetails`）；只公开明确审核过的列。
- 保留交易所原生 `orderID`、`execID`，便于跨表关联；这些关联不需要客户端自定义 ID。
- `/api/v1/user` 账户资料与 API 凭据始终不公开。

## 派生收益曲线的方法

`derived-equity-curve.csv` 刻意做得简单、可审计：

1. 它跟踪的是 **XBT + USDt 两个钱包合并后的 XBT 等值财富**。
2. 基准点定义为：首个交易日里，最后一次完成入金之后的第一笔完整 XBT 钱包余额。
3. 从这个基准点开始，**完成出金会加回去**，**完成入金会扣掉**，并且会把内部 `Transfer` 行中和掉。
4. `Conversion` 以及 XBT/USDt 的 `SpotTrade` 成对记录按**内部换仓**处理，不视为财富损失。
5. USDt 余额会按公开钱包账本里最近一次观察到的内部 XBT/USDT 转换或现货成交汇率折回 XBT。
6. 对钱包账本驱动的现金流事件，如果 BitMEX 同时给出 `timestamp` 和 `transactTime`，排序会优先使用 `timestamp`；`transactTime` 仍保留为交易所原始字段，但不会被盲目当成会计生效顺序。
7. 所以这条曲线是一个方便公众阅读的 **XBT 等值财富曲线**，**不是** 覆盖所有非 XBT 钱包、所有资产、所有时刻的完整逐时盯市净值。

更具体地说，这个账号在 BitMEX 上的绝大部分交易，本质上都是以 XBT 结算结果为主：按 executed trade notional 并按结算货币分组，大约 98.9% 结算在 XBT，只有约 1.1% 结算在 USDt。所以这条曲线里的盈亏变化，本质上主要来自 XBT 数量和 XBT 计价价值的变化，USDt 只是一个很小的补充层。唯一的完成外部入金，就是 2020-05-01 的两笔初始 XBT 入金，之后到现在没有新的完成入金。

这样做的好处是：方法足够透明，而且能避免账户在 XBT 和 USDt 之间临时切换时出现假的断崖。

## 明确不放进这个仓库的内容

- 原始 API key / secret
- `/api/v1/user` 个人资料 payload
- 客户端自定义订单标识及未经审核的 execution 自由文本字段
- 登录/IP/设备/账户资料类信息
- `walletHistory` 里的链上 tx hash

## 更新策略

本次是应账户所有者要求进行的最后一次归档刷新，之后不再计划例行更新。它是有明确截止时间的快照，不包含未来账户活动。以下更新流程保留用于复现与审计。

每次更新应当：

1. 从 BitMEX 拉取最新全量 raw 数据，
2. 用同样的文件名和同样的隐私规则重建 public root，
3. 提交新的根目录版本，
4. 打上 `data-YYYY-MM-DD` 的 tag。

这样一来，读者看到的是稳定文件名；而历史变化则通过 Git 历史和 tag 完整追溯。
