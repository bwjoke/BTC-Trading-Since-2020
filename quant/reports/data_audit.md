# M0-01 数据集审计报告

生成时间（UTC）：`2026-08-19T02:44:51.759122Z`
数据版本 commit：`f02a691c7f7cfd0cd08ffb7f13a656ebaf2c6ca6`
分析分支：`quant/m0-data-audit`

## 执行摘要

- Manifest 文件检查：**11 PASS / 2 WARNING / 0 FAIL**。
- M0-02 仓位重建判断：**READY_WITH_WARNINGS**。
- 订单数：`43,251`；成交数：`173,434`；钱包事件数：`17,484`。
- 本阶段只读原始数据，未训练模型、未连接交易所、未进行自动修复。

## 数据文件清单

| 文件 | Manifest | 数据 | 实际行数 | 字节数 |
| --- | --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | PASS | WARNING | 173434 | 68562804 |
| api-v1-order.csv | PASS | WARNING | 43251 | 7798385 |
| api-v1-user-walletHistory.csv | PASS | WARNING | 17484 | 2809134 |
| api-v1-position.snapshot.csv | PASS | WARNING | 1 | 1088 |
| api-v1-user-wallet.snapshot-all.csv | PASS | WARNING | 15 | 897 |
| api-v1-user-margin.snapshot-all.csv | PASS | WARNING | 3 | 890 |
| api-v1-user-walletSummary.all.csv | PASS | WARNING | 80 | 4911 |
| api-v1-instrument.all.csv | PASS | WARNING | 3090 | 1248491 |
| api-v1-wallet-assets.csv | PASS | WARNING | 52 | 17492 |
| derived-equity-curve.csv | PASS | WARNING | 17468 | 4186724 |
| cumulative-performance.png | PASS | N/A | N/A | 137427 |
| README.md | WARNING | N/A | N/A | 9934 |
| README.zh-CN.md | WARNING | N/A | N/A | 9756 |

## Manifest 一致性

每个文件均按存在性、文件大小、SHA256、声明列名、声明行数和时间范围核对。
| 文件 | 结果 | 失败检查 |
| --- | --- | --- |
| api-v1-execution-tradeHistory.csv | PASS | 全部通过 |
| api-v1-order.csv | PASS | 全部通过 |
| api-v1-user-walletHistory.csv | PASS | 全部通过 |
| api-v1-position.snapshot.csv | PASS | 全部通过 |
| api-v1-user-wallet.snapshot-all.csv | PASS | 全部通过 |
| api-v1-user-margin.snapshot-all.csv | PASS | 全部通过 |
| api-v1-user-walletSummary.all.csv | PASS | 全部通过 |
| api-v1-instrument.all.csv | PASS | 全部通过 |
| api-v1-wallet-assets.csv | PASS | 全部通过 |
| derived-equity-curve.csv | PASS | 全部通过 |
| cumulative-performance.png | PASS | 全部通过 |
| README.md | WARNING | size_bytes, sha256 |
| README.zh-CN.md | WARNING | size_bytes, sha256 |

## 字段与行数检查

| 文件 | 状态 | 行数 | 列数 | 最早时间 | 最晚时间 |
| --- | --- | --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | WARNING | 173434 | 40 | 2020-05-01T09:03:47.36Z | 2026-07-19T12:00:00.33Z |
| api-v1-order.csv | WARNING | 43251 | 22 | 2020-05-01T09:03:47.36Z | 2026-07-18T22:11:15.557Z |
| api-v1-user-walletHistory.csv | WARNING | 17484 | 13 | 2020-05-01T01:05:55.004Z | 2026-07-19T12:35:02.029Z |
| api-v1-position.snapshot.csv | WARNING | 1 | 55 | 2026-07-19T12:35:00.504Z | 2026-07-19T12:35:00.504Z |
| api-v1-user-wallet.snapshot-all.csv | WARNING | 15 | 10 | 2025-11-25T09:22:52.847Z | 2026-07-19T12:00:00.33Z |
| api-v1-user-margin.snapshot-all.csv | WARNING | 3 | 25 | 2026-04-29T02:09:35.36Z | 2026-07-19T12:35:00.504Z |
| api-v1-user-walletSummary.all.csv | WARNING | 80 | 10 |  |  |
| api-v1-instrument.all.csv | WARNING | 3090 | 98 | 2014-11-21T21:00:02.409Z | 2026-07-19T12:35:03.897Z |
| api-v1-wallet-assets.csv | WARNING | 52 | 14 |  |  |
| derived-equity-curve.csv | WARNING | 17468 | 21 | 2020-05-01T14:39:40.387Z | 2026-07-19T12:35:02.029Z |

### `api-v1-execution-tradeHistory.csv` 列名

```text
timestamp,transactTime,execType,ordStatus,symbol,side,orderQty,lastQty,leavesQty,price,lastPx,avgPx,currency,settlCurrency,execCost,execComm,realisedPnl,homeNotional,foreignNotional,orderID,execID,trdMatchID,text,brokerCommission,brokerExecComm,commission,cumQty,displayQty,execCommCcy,execInst,feeType,lastLiquidityInd,ordType,pool,stopPx,strategy,timeInForce,tradePublishIndicator,triggered,workingIndicator
```

### `api-v1-order.csv` 列名

```text
timestamp,transactTime,ordStatus,ordType,symbol,side,orderQty,cumQty,leavesQty,price,avgPx,stopPx,timeInForce,execInst,displayQty,workingIndicator,triggered,orderID,currency,ordRejReason,settlCurrency,strategy
```

### `api-v1-user-walletHistory.csv` 列名

```text
timestamp,transactTime,transactType,transactStatus,currency,network,amount,fee,walletBalance,orderID,transactID,address,marginBalance
```

## 时间范围与顺序

| 文件 | 字段 | 非空 | 解析失败 | 乱序数 | 最早 | 最晚 |
| --- | --- | --- | --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | timestamp | 173434 | 0 | 10 | 2020-05-01T09:03:47.36Z | 2026-07-19T12:00:00.33Z |
| api-v1-execution-tradeHistory.csv | transactTime | 173434 | 0 | 0 | 2020-05-01T09:03:47.36Z | 2026-07-19T12:00:00.33Z |
| api-v1-order.csv | timestamp | 43251 | 0 | 0 | 2020-05-01T09:03:47.36Z | 2026-07-18T22:11:15.557Z |
| api-v1-order.csv | transactTime | 43251 | 0 | 10501 | 2020-05-01T09:03:38.162Z | 2026-07-18T22:11:15.556Z |
| api-v1-user-walletHistory.csv | timestamp | 17484 | 0 | 0 | 2020-05-01T01:05:55.004Z | 2026-07-19T12:35:02.029Z |
| api-v1-user-walletHistory.csv | transactTime | 17484 | 0 | 5 | 2020-05-01T01:05:55.004Z | 2026-07-19T12:35:02.029Z |
| api-v1-position.snapshot.csv | timestamp | 1 | 0 | 0 | 2026-07-19T12:35:00.504Z | 2026-07-19T12:35:00.504Z |
| api-v1-user-wallet.snapshot-all.csv | timestamp | 15 | 0 | 14 | 2025-11-25T09:22:52.847Z | 2026-07-19T12:00:00.33Z |
| api-v1-user-margin.snapshot-all.csv | timestamp | 3 | 0 | 0 | 2026-04-29T02:09:35.36Z | 2026-07-19T12:35:00.504Z |
| api-v1-instrument.all.csv | listing | 880 | 0 | 0 | 2014-11-21T20:00:00Z | 2200-02-01T00:00:00Z |
| api-v1-instrument.all.csv | expiry | 787 | 0 | 222 | 2014-11-21T20:00:00Z | 2027-03-26T12:00:00Z |
| api-v1-instrument.all.csv | settle | 787 | 0 | 221 | 2014-11-21T20:00:00Z | 2027-03-26T12:00:00Z |
| api-v1-instrument.all.csv | closingTimestamp | 880 | 0 | 246 | 2014-11-21T20:00:00Z | 2200-02-01T01:00:00Z |
| api-v1-instrument.all.csv | fundingTimestamp | 328 | 0 | 102 | 2016-11-04T12:00:00Z | 2026-07-19T20:00:00Z |
| api-v1-instrument.all.csv | openingTimestamp | 880 | 0 | 246 | 2014-11-21T20:00:00Z | 2200-02-01T00:00:00Z |
| api-v1-instrument.all.csv | publishTime | 893 | 0 | 1 | 2000-01-01T07:30:00Z | 2000-01-01T12:00:00Z |
| api-v1-instrument.all.csv | rebalanceTimestamp | 8 | 0 | 3 | 2016-06-24T12:00:00Z | 2016-09-30T12:00:00Z |
| api-v1-instrument.all.csv | timestamp | 3090 | 0 | 916 | 2014-11-21T21:00:02.409Z | 2026-07-19T12:35:03.897Z |
| derived-equity-curve.csv | timestamp | 17468 | 0 | 0 | 2020-05-01T14:39:40.387Z | 2026-07-19T12:35:02.029Z |
| derived-equity-curve.csv | transactTime | 17468 | 0 | 5 | 2020-05-01T14:39:40.387Z | 2026-07-19T12:35:02.029Z |
| derived-equity-curve.csv | baselineTimestamp | 17468 | 0 | 0 | 2020-05-01T14:39:40.387Z | 2020-05-01T14:39:40.387Z |

## 主键质量

| 文件 | 主键 | 非空唯一值 | 空值 | 重复行 | 重复键值 | 重复分类 |
| --- | --- | --- | --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | execID | 173434 | 0 | 0 | 0 | {} |
| api-v1-order.csv | orderID | 43216 | 0 | 35 | 35 | {'exact_duplicate_rows': 35} |
| api-v1-user-walletHistory.csv | transactID | 17483 | 1 | 0 | 0 | {} |

重复 `orderID` 分析：同一 `orderID` 多行不能直接视为脏数据；报告将状态、symbol、side、时间跨度不同的组标记为 `likely_lifecycle_records`，并保留其行。

### `api-v1-order.csv` 重复键示例（最多 200 组）

| 键 | 行数 | 状态 | 时间范围 | 分类 | 首末行 |
| --- | --- | --- | --- | --- | --- |
| 09497f00-9bc7-4d89-a64f-a006eb462bf6 | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16471 → 16506 |
| 0df81572-f26c-43d9-943c-18b3c1a65683 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17489 → 17515 |
| 23a3dcc5-5969-40a5-b10b-b70aa83e71f3 | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16458 → 16502 |
| 3187d027-a459-4a00-bf9b-d0e8dd231073 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17481 → 17510 |
| 325b3db5-43ea-4b30-9064-f02320618502 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17471 → 17502 |
| 44a91aee-b46a-4b93-ad26-281be24666d8 | 2 | {'Canceled': 2} | 2021-05-28T04:57:39.189Z → 2021-05-28T04:57:39.189Z | exact_duplicate_rows | 19993 → 20002 |
| 44abeb3c-db9a-45b8-84f2-511e7f58c5f0 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17496 → 17508 |
| 48654e03-6e81-41c3-9db0-a4730147d2cc | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16470 → 16507 |
| 4a6ab3d3-242b-4920-9996-4d9ee9fc4ae8 | 2 | {'Canceled': 2} | 2021-05-28T04:57:39.189Z → 2021-05-28T04:57:39.189Z | exact_duplicate_rows | 19996 → 20006 |
| 5028eb7d-e2af-4e58-90fb-5ce23b0b1fe3 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17494 → 17511 |
| 5774df16-2761-438e-8194-e17166a1d172 | 2 | {'Canceled': 2} | 2021-03-09T21:23:39.537Z → 2021-03-09T21:23:39.537Z | exact_duplicate_rows | 15488 → 15505 |
| 60c1684f-e41e-4f3b-971b-05970c8ef5d0 | 2 | {'Canceled': 2} | 2021-05-28T04:57:39.189Z → 2021-05-28T04:57:39.189Z | exact_duplicate_rows | 19991 → 20004 |
| 68efb4b6-beae-4fc9-93f9-b07284b8f064 | 2 | {'Canceled': 2} | 2021-05-28T04:57:39.189Z → 2021-05-28T04:57:39.189Z | exact_duplicate_rows | 19992 → 20003 |
| 7d97a7e2-9ea8-402f-9feb-3207e4008c36 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17490 → 17514 |
| 87ba1cf5-88ff-45bf-88c2-9b41d28469b3 | 2 | {'Canceled': 2} | 2021-03-09T21:23:39.537Z → 2021-03-09T21:23:39.537Z | exact_duplicate_rows | 15498 → 15502 |
| 8ca031a0-8d37-4a98-a08c-da8eaae589df | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16463 → 16503 |
| 93bce7f1-ae8d-4971-8e60-ed9e80236c38 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17488 → 17516 |
| a025b0ca-9360-46e3-85f4-a240f0bc68aa | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17498 → 17504 |
| a66dfa87-974f-4816-acf1-da337e0f73eb | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17497 → 17505 |
| aeca8537-14c7-44ca-be8b-b38e5e9846c4 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17480 → 17509 |
| b0c2a368-e54b-4feb-9b4a-2ae3f74f0c59 | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16481 → 16505 |
| b4eb2314-fce7-49a4-a0ff-61dbb72b1c4d | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17482 → 17507 |
| b9806364-746d-4075-b64f-4504277587f4 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17492 → 17513 |
| bc6a0adc-8e90-4206-9ac9-1414a99d953e | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17485 → 17519 |
| c0588198-f772-4aba-97e3-dc7afea3496b | 2 | {'Canceled': 2} | 2021-01-04T10:57:04.689Z → 2021-01-04T10:57:04.689Z | exact_duplicate_rows | 7500 → 7505 |
| c628ed12-2fce-45dd-8377-e648e6e04631 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17486 → 17518 |
| c835ddc0-35e5-4b36-9465-7bd18a6d3dce | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17478 → 17503 |
| c8a920be-1c68-4126-ac50-38f0186e188e | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16477 → 16508 |
| e4aa304a-a039-4b59-a9ea-26a16a232e33 | 2 | {'Canceled': 2} | 2021-05-28T04:57:39.189Z → 2021-05-28T04:57:39.189Z | exact_duplicate_rows | 19998 → 20005 |
| e6063bf1-7116-4f73-a07c-384e1045d3b6 | 2 | {'Canceled': 2} | 2021-03-28T18:47:12.783Z → 2021-03-28T18:47:12.783Z | exact_duplicate_rows | 16472 → 16504 |
| ec3d5421-3a98-4075-bd23-954cf497924b | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17487 → 17517 |
| f3107d9a-1c76-42e8-96e0-09ca95de2221 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17493 → 17512 |
| f311a532-d99d-4254-bf87-82ff7cb98b73 | 2 | {'Canceled': 2} | 2021-01-04T10:57:04.689Z → 2021-01-04T10:57:04.689Z | exact_duplicate_rows | 7501 → 7504 |
| f7272149-a659-420d-bd0c-5f0c19a37f4c | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17479 → 17506 |
| ff4b2e74-d69d-4221-a924-39fb0a4c3df5 | 2 | {'Canceled': 2} | 2021-04-21T20:29:58.243Z → 2021-04-21T20:29:58.243Z | exact_duplicate_rows | 17484 → 17520 |

## 表关联覆盖率

| 指标 | 值 |
| --- | --- |
| 成交行数 | 173434 |
| 成交 orderID 非空行数 | 160478 |
| 成交 orderID 空值行数 | 12956 |
| 成交 orderID 非空比例 | 92.5297% |
| 按非空成交行的 orderID 关联率 | 99.9938% |
| 订单表唯一 orderID | 43216 |
| 成交表唯一 orderID | 31717 |
| 成交 orderID 匹配唯一值 | 31716 |
| 成交 orderID 未匹配唯一值 | 1 |
| 唯一 orderID 关联率 | 99.9968% |

未匹配 orderID 示例：

```text
18a1e0fe-da52-40eb-8e51-e2acbded0578
```

## 缺失值

以下列出每个文件的非零缺失列；比例按该文件数据行数计算。
| 文件 | 字段 | 缺失数 | 缺失比例 |
| --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | avgPx | 3 | 0.0017% |
| api-v1-execution-tradeHistory.csv | brokerCommission | 162326 | 93.5953% |
| api-v1-execution-tradeHistory.csv | brokerExecComm | 162326 | 93.5953% |
| api-v1-execution-tradeHistory.csv | displayQty | 171951 | 99.1449% |
| api-v1-execution-tradeHistory.csv | execCommCcy | 172297 | 99.3444% |
| api-v1-execution-tradeHistory.csv | execInst | 161972 | 93.3911% |
| api-v1-execution-tradeHistory.csv | feeType | 147067 | 84.7971% |
| api-v1-execution-tradeHistory.csv | lastLiquidityInd | 9896 | 5.7059% |
| api-v1-execution-tradeHistory.csv | leavesQty | 2500 | 1.4415% |
| api-v1-execution-tradeHistory.csv | orderID | 12956 | 7.4703% |
| api-v1-execution-tradeHistory.csv | price | 7769 | 4.4795% |
| api-v1-execution-tradeHistory.csv | realisedPnl | 157695 | 90.9251% |
| api-v1-execution-tradeHistory.csv | settlCurrency | 208 | 0.1199% |
| api-v1-execution-tradeHistory.csv | side | 12905 | 7.4409% |
| api-v1-execution-tradeHistory.csv | stopPx | 172352 | 99.3761% |
| api-v1-execution-tradeHistory.csv | strategy | 170880 | 98.5274% |
| api-v1-execution-tradeHistory.csv | tradePublishIndicator | 12908 | 7.4426% |
| api-v1-execution-tradeHistory.csv | triggered | 172383 | 99.3940% |
| api-v1-order.csv | avgPx | 11535 | 26.6699% |
| api-v1-order.csv | displayQty | 43056 | 99.5491% |
| api-v1-order.csv | execInst | 42066 | 97.2602% |
| api-v1-order.csv | ordRejReason | 43065 | 99.5700% |
| api-v1-order.csv | orderQty | 3 | 0.0069% |
| api-v1-order.csv | price | 936 | 2.1641% |
| api-v1-order.csv | settlCurrency | 92 | 0.2127% |
| api-v1-order.csv | side | 3 | 0.0069% |
| api-v1-order.csv | stopPx | 43136 | 99.7341% |
| api-v1-order.csv | triggered | 43170 | 99.8127% |
| api-v1-user-walletHistory.csv | address | 2 | 0.0114% |
| api-v1-user-walletHistory.csv | fee | 2808 | 16.0604% |
| api-v1-user-walletHistory.csv | marginBalance | 17483 | 99.9943% |
| api-v1-user-walletHistory.csv | network | 17478 | 99.9657% |
| api-v1-user-walletHistory.csv | orderID | 10002 | 57.2066% |
| api-v1-user-walletHistory.csv | transactID | 1 | 0.0057% |
| api-v1-position.snapshot.csv | marginCallPrice | 1 | 100.0000% |
| api-v1-position.snapshot.csv | openingQty | 1 | 100.0000% |
| api-v1-position.snapshot.csv | positionReport | 1 | 100.0000% |
| api-v1-position.snapshot.csv | prevUnrealisedPnl | 1 | 100.0000% |
| api-v1-user-margin.snapshot-all.csv | isolatedUnrealisedPnl | 3 | 100.0000% |
| api-v1-user-margin.snapshot-all.csv | riskLimit | 1 | 33.3333% |
| api-v1-user-walletSummary.all.csv | symbol | 14 | 17.5000% |
| api-v1-instrument.all.csv | askPrice | 2359 | 76.3430% |
| api-v1-instrument.all.csv | bidPrice | 2352 | 76.1165% |
| api-v1-instrument.all.csv | calcInterval | 2192 | 70.9385% |
| api-v1-instrument.all.csv | closingTimestamp | 2210 | 71.5210% |
| api-v1-instrument.all.csv | expiry | 2303 | 74.5307% |
| api-v1-instrument.all.csv | fairBasis | 2301 | 74.4660% |
| api-v1-instrument.all.csv | fairBasisRate | 2309 | 74.7249% |
| api-v1-instrument.all.csv | fairMethod | 2343 | 75.8252% |
| api-v1-instrument.all.csv | fairPrice | 2259 | 73.1068% |
| api-v1-instrument.all.csv | foreignNotional24h | 2210 | 71.5210% |
| api-v1-instrument.all.csv | front | 2243 | 72.5890% |
| api-v1-instrument.all.csv | fundingBaseRate | 2860 | 92.5566% |
| api-v1-instrument.all.csv | fundingBaseSymbol | 2765 | 89.4822% |
| api-v1-instrument.all.csv | fundingInterval | 2762 | 89.3851% |
| api-v1-instrument.all.csv | fundingPremiumSymbol | 2764 | 89.4498% |
| api-v1-instrument.all.csv | fundingQuoteRate | 2860 | 92.5566% |
| api-v1-instrument.all.csv | fundingQuoteSymbol | 2765 | 89.4822% |
| api-v1-instrument.all.csv | fundingRate | 2764 | 89.4498% |
| api-v1-instrument.all.csv | fundingTimestamp | 2762 | 89.3851% |
| api-v1-instrument.all.csv | highPrice | 2970 | 96.1165% |
| api-v1-instrument.all.csv | homeNotional24h | 2210 | 71.5210% |
| api-v1-instrument.all.csv | impactAskPrice | 2625 | 84.9515% |
| api-v1-instrument.all.csv | impactBidPrice | 2625 | 84.9515% |
| api-v1-instrument.all.csv | impactMidPrice | 2625 | 84.9515% |
| api-v1-instrument.all.csv | indicativeFundingRate | 2764 | 89.4498% |
| api-v1-instrument.all.csv | indicativeSettlePrice | 2272 | 73.5275% |
| api-v1-instrument.all.csv | initMargin | 2234 | 72.2977% |
| api-v1-instrument.all.csv | lastChangePcnt | 120 | 3.8835% |
| api-v1-instrument.all.csv | lastPrice | 66 | 2.1359% |
| api-v1-instrument.all.csv | lastPriceProtected | 2234 | 72.2977% |
| api-v1-instrument.all.csv | lastTickDirection | 1439 | 46.5696% |
| api-v1-instrument.all.csv | limit | 3034 | 98.1877% |
| api-v1-instrument.all.csv | limitDownPrice | 3017 | 97.6375% |
| api-v1-instrument.all.csv | limitUpPrice | 3017 | 97.6375% |
| api-v1-instrument.all.csv | listedSettle | 2578 | 83.4304% |
| api-v1-instrument.all.csv | listing | 2210 | 71.5210% |
| api-v1-instrument.all.csv | lotSize | 2210 | 71.5210% |
| api-v1-instrument.all.csv | lowPrice | 2970 | 96.1165% |
| api-v1-instrument.all.csv | maintMargin | 2234 | 72.2977% |
| api-v1-instrument.all.csv | makerFee | 2210 | 71.5210% |
| api-v1-instrument.all.csv | markMethod | 16 | 0.5178% |
| api-v1-instrument.all.csv | markPrice | 65 | 2.1036% |
| api-v1-instrument.all.csv | maxOrderQty | 2210 | 71.5210% |
| api-v1-instrument.all.csv | maxPrice | 2210 | 71.5210% |
| api-v1-instrument.all.csv | midPrice | 2358 | 76.3107% |
| api-v1-instrument.all.csv | minTick | 2261 | 73.1715% |
| api-v1-instrument.all.csv | multiplier | 2210 | 71.5210% |
| api-v1-instrument.all.csv | openInterest | 2168 | 70.1618% |
| api-v1-instrument.all.csv | openValue | 1460 | 47.2492% |
| api-v1-instrument.all.csv | openingTimestamp | 2210 | 71.5210% |
| api-v1-instrument.all.csv | pool | 2941 | 95.1780% |
| api-v1-instrument.all.csv | positionCurrency | 2453 | 79.3851% |
| api-v1-instrument.all.csv | prevClosePrice | 2233 | 72.2654% |
| api-v1-instrument.all.csv | prevPrice24h | 2264 | 73.2686% |
| api-v1-instrument.all.csv | prevTotalTurnover | 2215 | 71.6828% |
| api-v1-instrument.all.csv | prevTotalVolume | 2215 | 71.6828% |
| api-v1-instrument.all.csv | publishInterval | 880 | 28.4790% |
| api-v1-instrument.all.csv | publishTime | 2197 | 71.1003% |
| api-v1-instrument.all.csv | quoteToSettleMultiplier | 2396 | 77.5405% |
| api-v1-instrument.all.csv | rebalanceInterval | 3082 | 99.7411% |
| api-v1-instrument.all.csv | rebalanceTimestamp | 3082 | 99.7411% |
| api-v1-instrument.all.csv | reference | 23 | 0.7443% |
| api-v1-instrument.all.csv | referenceSymbol | 31 | 1.0032% |
| api-v1-instrument.all.csv | riskLimit | 2274 | 73.5922% |
| api-v1-instrument.all.csv | riskStep | 2274 | 73.5922% |
| api-v1-instrument.all.csv | settlCurrency | 2247 | 72.7184% |
| api-v1-instrument.all.csv | settle | 2303 | 74.5307% |
| api-v1-instrument.all.csv | settledPrice | 2362 | 76.4401% |
| api-v1-instrument.all.csv | settledPriceAdjustmentRate | 3067 | 99.2557% |
| api-v1-instrument.all.csv | settlementFee | 2219 | 71.8123% |
| api-v1-instrument.all.csv | takerFee | 2210 | 71.5210% |
| api-v1-instrument.all.csv | totalTurnover | 2215 | 71.6828% |
| api-v1-instrument.all.csv | totalVolume | 2215 | 71.6828% |
| api-v1-instrument.all.csv | turnover | 2215 | 71.6828% |
| api-v1-instrument.all.csv | turnover24h | 2210 | 71.5210% |
| api-v1-instrument.all.csv | underlyingSymbol | 51 | 1.6505% |
| api-v1-instrument.all.csv | underlyingToPositionMultiplier | 2524 | 81.6828% |
| api-v1-instrument.all.csv | underlyingToSettleMultiplier | 2900 | 93.8511% |
| api-v1-instrument.all.csv | volume | 2215 | 71.6828% |
| api-v1-instrument.all.csv | volume24h | 2210 | 71.5210% |
| api-v1-instrument.all.csv | vwap | 3001 | 97.1197% |
| api-v1-wallet-assets.csv | maxWithdrawalAmount | 1 | 1.9231% |
| api-v1-wallet-assets.csv | minDepositAmount | 1 | 1.9231% |
| api-v1-wallet-assets.csv | minWithdrawalAmount | 1 | 1.9231% |
| derived-equity-curve.csv | adjustedMarkedMultipleVsBaseline | 17467 | 99.9943% |
| derived-equity-curve.csv | adjustedMarkedWealthXBT | 17467 | 99.9943% |
| derived-equity-curve.csv | marginBalanceXBT | 17467 | 99.9943% |
| derived-equity-curve.csv | marginBalanceXBTEquivalent | 17467 | 99.9943% |
| derived-equity-curve.csv | reference | 1 | 0.0057% |
| derived-equity-curve.csv | xbtUsdtRate | 2537 | 14.5237% |

## 重复数据

| 文件 | 行数 | 完全重复行（首行后） | 主键重复行 |
| --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | 173434 | 0 | 0 |
| api-v1-order.csv | 43251 | 35 | 35 |
| api-v1-user-walletHistory.csv | 17484 | 0 | 0 |
| api-v1-position.snapshot.csv | 1 | 0 | N/A |
| api-v1-user-wallet.snapshot-all.csv | 15 | 0 | N/A |
| api-v1-user-margin.snapshot-all.csv | 3 | 0 | N/A |
| api-v1-user-walletSummary.all.csv | 80 | 0 | N/A |
| api-v1-instrument.all.csv | 3090 | 0 | N/A |
| api-v1-wallet-assets.csv | 52 | 0 | N/A |
| derived-equity-curve.csv | 17468 | 0 | N/A |

## 枚举值分布

### `api-v1-execution-tradeHistory.csv`

**execType**

| 值 | 频次 |
| --- | --- |
| Funding | 12905 |
| Settlement | 19 |
| Trade | 160510 |

**ordStatus**

| 值 | 频次 |
| --- | --- |
| Filled | 44219 |
| PartiallyFilled | 129215 |

**side**

| 值 | 频次 |
| --- | --- |
| <MISSING> | 12905 |
| Buy | 77559 |
| Sell | 82970 |

**symbol**

| 值 | 频次 |
| --- | --- |
| AAVEUSDT | 567 |
| ADAM20 | 366 |
| ADAUSD | 575 |
| ADAUSDT | 155 |
| ALTMEXUSD | 70 |
| AXSUSDT | 919 |
| BCHH21 | 101 |
| BCHUSD | 154 |
| BMEXUSD | 143 |
| BMEX_USDT | 201 |
| BNBUSD | 28 |
| BNBUSDT | 185 |
| DOGEUSD | 5924 |
| DOGEUSDT | 2068 |
| DOTUSDT | 3506 |
| DOTUSDTH21 | 49 |
| EOSH21 | 37 |
| EOSUSDTZ20 | 7 |
| ETHH21 | 1138 |
| ETHH22 | 477 |
| ETHH23 | 391 |
| ETHH24 | 35 |
| ETHM20 | 86 |
| ETHM21 | 178 |
| ETHM22 | 234 |
| ETHM23 | 351 |
| ETHM24 | 282 |
| ETHU20 | 221 |
| ETHU21 | 476 |
| ETHU22 | 47 |
| ETHU23 | 180 |
| ETHU24 | 157 |
| ETHUSD | 19470 |
| ETHUSDZ20 | 8 |
| ETHZ20 | 1168 |
| ETHZ21 | 870 |
| ETHZ22 | 182 |
| ETHZ23 | 271 |
| ETHZ24 | 80 |
| LINKUSDT | 253 |
| LINKUSDTZ20 | 16 |
| LTCH21 | 1414 |
| LTCM20 | 387 |
| LTCM21 | 172 |
| LTCU20 | 316 |
| LTCU21 | 418 |
| LTCUSD | 7473 |
| LTCZ20 | 816 |
| LTCZ21 | 122 |
| LUNAUSD | 428 |
| ORDIUSD | 407 |
| TRXH21 | 2218 |
| TRXM20 | 137 |
| TRXM21 | 1468 |
| TRXU20 | 771 |
| TRXU21 | 1759 |
| TRXUSDT | 27 |
| TRXZ20 | 498 |
| TRXZ21 | 124 |
| UNIUSDT | 889 |
| XBTM21 | 19 |
| XBTUSD | 104880 |
| XBT_USDT | 7 |
| XLMUSDT | 54 |
| XRPUSD | 6128 |
| XTZUSDTZ20 | 9 |
| YFIUSDTH21 | 359 |
| YFIUSDTZ20 | 508 |

**lastLiquidityInd**

| 值 | 频次 |
| --- | --- |
| <MISSING> | 9896 |
| AddedLiquidity | 74586 |
| RemovedLiquidity | 88952 |

### `api-v1-order.csv`

**ordStatus**

| 值 | 频次 |
| --- | --- |
| Canceled | 11783 |
| Filled | 31262 |
| New | 20 |
| Rejected | 186 |

**ordType**

| 值 | 频次 |
| --- | --- |
| Limit | 35238 |
| Market | 7898 |
| Stop | 114 |
| StopLimit | 1 |

**side**

| 值 | 频次 |
| --- | --- |
| <MISSING> | 3 |
| Buy | 23749 |
| Sell | 19499 |

**symbol**

| 值 | 频次 |
| --- | --- |
| AAVEUSDT | 123 |
| ADAM20 | 125 |
| ADAUSD | 20 |
| ADAUSDT | 8 |
| ALTMEXUSD | 35 |
| AXSUSDT | 113 |
| BCHH21 | 18 |
| BCHUSD | 54 |
| BMEXUSD | 49 |
| BMEX_USDT | 90 |
| BNBUSD | 23 |
| BNBUSDT | 39 |
| DOGEUSD | 1392 |
| DOGEUSDT | 416 |
| DOTUSDT | 159 |
| DOTUSDTH21 | 45 |
| EOSH21 | 4 |
| EOSUSDTZ20 | 2 |
| ETHH21 | 373 |
| ETHH22 | 179 |
| ETHH23 | 254 |
| ETHH24 | 46 |
| ETHM20 | 14 |
| ETHM21 | 76 |
| ETHM22 | 198 |
| ETHM23 | 221 |
| ETHM24 | 87 |
| ETHU20 | 52 |
| ETHU21 | 86 |
| ETHU22 | 45 |
| ETHU23 | 86 |
| ETHU24 | 45 |
| ETHUSD | 5082 |
| ETHUSDZ20 | 2 |
| ETHZ20 | 288 |
| ETHZ21 | 465 |
| ETHZ22 | 77 |
| ETHZ23 | 135 |
| ETHZ24 | 38 |
| LINKUSDT | 40 |
| LINKUSDTZ20 | 6 |
| LTCH21 | 174 |
| LTCM20 | 18 |
| LTCM21 | 12 |
| LTCU20 | 92 |
| LTCU21 | 21 |
| LTCUSD | 1841 |
| LTCZ20 | 113 |
| LTCZ21 | 19 |
| LUNAUSD | 134 |
| ORDIUSD | 11 |
| TRXH21 | 182 |
| TRXM20 | 55 |
| TRXM21 | 256 |
| TRXU20 | 256 |
| TRXU21 | 83 |
| TRXUSDT | 15 |
| TRXZ20 | 91 |
| TRXZ21 | 35 |
| UNIUSDT | 77 |
| XBTM21 | 2 |
| XBTUSD | 27267 |
| XBT_USDT | 2 |
| XLMUSDT | 6 |
| XRPUSD | 1545 |
| XTZUSDTZ20 | 15 |
| YFIUSDTH21 | 88 |
| YFIUSDTZ20 | 231 |

### `api-v1-user-walletHistory.csv`

**transactType**

| 值 | 频次 |
| --- | --- |
| Conversion | 24 |
| Deposit | 2 |
| Funding | 2057 |
| RealisedPNL | 15021 |
| SpotTrade | 320 |
| Transfer | 53 |
| UnrealisedPNL | 1 |
| Withdrawal | 6 |

**transactStatus**

| 值 | 频次 |
| --- | --- |
| Canceled | 1 |
| Completed | 17482 |
| Pending | 1 |

**currency**

| 值 | 频次 |
| --- | --- |
| BMEx | 174 |
| USDt | 198 |
| XBt | 17112 |

## 数值异常

| 文件 | 非正价格 | 负数量 | lastQty>orderQty | cumQty>orderQty | leavesQty<0 | 有量无成交价 | 余额跳变候选 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-order.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-user-walletHistory.csv | {} | {} | 0 | 0 | 0 | 0 | 20 |
| api-v1-position.snapshot.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-user-wallet.snapshot-all.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-user-margin.snapshot-all.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-user-walletSummary.all.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-instrument.all.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| api-v1-wallet-assets.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |
| derived-equity-curve.csv | {} | {} | 0 | 0 | 0 | 0 | 0 |

### 极端数值（仅报告，不自动判断为错误）

| 文件 | 字段 | 有效数 | 最小 | 最大 | 绝对值 P99 | 绝对值最大示例 |
| --- | --- | --- | --- | --- | --- | --- |
| api-v1-execution-tradeHistory.csv | execCost | 173434 | -13372421855.0 | 11847861188.0 | 1999166895.85 | [{'absolute_value': 13372421855.0, 'line': 56959, 'value': -13372421855.0, 'timestamp': '2021-03-18T20:00:00.002Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'execID': '39e23b83-0a68-6f3d-427d-8eec334de508'}, {'absolute_value': 12431904375.0, 'line': 64316, 'value': -12431904375.0, 'timestamp': '2021-04-18T12:00:00.002Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'execID': '80c0afcc-a758-2d83-0f93-eb90092762ea'}, {'absolute_value': 12287446038.0, 'line': 71598, 'value': -12287446038.0, 'timestamp': '2021-05-12T20:00:00.000Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'execID': 'cca8ba9f-9bb6-e77f-cca0-d9bfe7392708'}] |
| api-v1-execution-tradeHistory.csv | execComm | 173434 | -7454007.0 | 19309802.0 | 430664.85 | [{'absolute_value': 19309802.0, 'line': 63437, 'value': 19309802.0, 'timestamp': '2021-04-10T20:00:00.002Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'execID': 'f7eff171-0c9b-6ab2-a8fd-c00d155f6508'}, {'absolute_value': 13560778.0, 'line': 75786, 'value': 13560778.0, 'timestamp': '2021-05-20T12:00:00.001Z', 'symbol': 'ETHUSD', 'currency': 'USD', 'execID': '500938c0-2ed0-becd-eea4-5caf8dd7cb20'}, {'absolute_value': 11247158.0, 'line': 63434, 'value': 11247158.0, 'timestamp': '2021-04-10T20:00:00.002Z', 'symbol': 'ETHUSD', 'currency': 'USD', 'execID': 'ab1ad994-cd21-9782-63a5-e6d338ca0093'}] |
| api-v1-execution-tradeHistory.csv | realisedPnl | 15739 | -6870867.0 | 46116212.0 | 4409628.74 | [{'absolute_value': 46116212.0, 'line': 167713, 'value': 46116212.0, 'timestamp': '2025-03-11T00:39:53.304Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'orderID': 'd6ce9dd4-4e85-4eb7-8437-6853d1ebb97b', 'execID': '00000000-006d-1000-0000-00148e48e351'}, {'absolute_value': 41173783.0, 'line': 173351, 'value': 41173783.0, 'timestamp': '2026-06-25T13:58:02.049Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'orderID': '555524bf-15bf-4ec3-8d9a-8508092be862', 'execID': '00000000-006d-1000-0000-0033c110b199'}, {'absolute_value': 34401733.0, 'line': 172413, 'value': 34401733.0, 'timestamp': '2026-01-31T18:38:29.529Z', 'symbol': 'XBTUSD', 'currency': 'USD', 'orderID': 'e2c4e32e-83ea-4d5c-94bd-174e99e0a59d', 'execID': '00000000-006d-1000-0000-0029c63efe6c'}] |
| api-v1-user-walletHistory.csv | amount | 17484 | -100000000000.0 | 74983620000.0 | 318128595.64 | [{'absolute_value': 100000000000.0, 'line': 2557, 'value': -100000000000.0, 'timestamp': '2022-02-22T16:48:10.411Z', 'currency': 'USDt', 'transactType': 'Conversion', 'transactID': '148c5c7f-f0c3-4df4-be1a-b95f7769ad52'}, {'absolute_value': 100000000000.0, 'line': 2561, 'value': -100000000000.0, 'timestamp': '2022-02-22T16:48:51.639Z', 'currency': 'USDt', 'transactType': 'Conversion', 'transactID': 'aeced366-78ca-4817-bb3d-4233735ebfd1'}, {'absolute_value': 100000000000.0, 'line': 2555, 'value': -100000000000.0, 'timestamp': '2022-02-22T16:47:58.175Z', 'currency': 'USDt', 'transactType': 'Conversion', 'transactID': 'ca6c686f-b23f-4d6a-a9a1-73b2e2c18941'}] |
| api-v1-user-walletHistory.csv | fee | 14676 | -2516254.0 | 1183922.0 | 286432.75 | [{'absolute_value': 2516254.0, 'line': 9839, 'value': -2516254.0, 'timestamp': '2024-12-05T20:00:00.140Z', 'currency': 'XBt', 'transactType': 'Funding', 'transactID': '00000000-0077-1000-0000-00001ee64d16'}, {'absolute_value': 1583909.0, 'line': 9837, 'value': -1583909.0, 'timestamp': '2024-12-05T12:00:00.186Z', 'currency': 'XBt', 'transactType': 'Funding', 'transactID': '00000000-0077-1000-0000-00001ecfec5d'}, {'absolute_value': 1538757.0, 'line': 9393, 'value': -1538757.0, 'timestamp': '2024-11-12T20:00:00.139Z', 'currency': 'XBt', 'transactType': 'Funding', 'transactID': '00000000-0077-1000-0000-000019e0852f'}] |
| api-v1-user-walletHistory.csv | walletBalance | 17484 | 0.0 | 470380300000.0 | 6695493687.0 | [{'absolute_value': 470380300000.0, 'line': 2554, 'value': 470380300000.0, 'timestamp': '2022-02-22T12:23:45.475Z', 'currency': 'USDt', 'transactType': 'Conversion', 'transactID': '0f05e90c-b1cb-66d1-b30e-1e4ae2c16dbc'}, {'absolute_value': 449377620000.0, 'line': 2552, 'value': 449377620000.0, 'timestamp': '2022-02-22T12:23:35.190Z', 'currency': 'USDt', 'transactType': 'Conversion', 'transactID': 'd05205d9-6ce5-6f3e-7e50-f38563dae3c3'}, {'absolute_value': 374608780000.0, 'line': 2550, 'value': 374608780000.0, 'timestamp': '2022-02-22T12:23:15.883Z', 'currency': 'USDt', 'transactType': 'Conversion', 'transactID': '745ed697-7068-f81c-f15c-5fb7ff0d4eb6'}] |
| api-v1-user-walletHistory.csv | marginBalance | 1 | 3380764154.0 | 3380764154.0 | 3380764154.0 | [{'absolute_value': 3380764154.0, 'line': 17485, 'value': 3380764154.0, 'timestamp': '2026-07-19T12:35:02.029Z', 'currency': 'XBt', 'transactType': 'UnrealisedPNL'}] |
| api-v1-position.snapshot.csv | realisedPnl | 1 | 0.0 | 0.0 | 0.0 | [{'absolute_value': 0.0, 'line': 2, 'value': 0.0, 'timestamp': '2026-07-19T12:35:00.504Z', 'symbol': 'XBTUSD', 'currency': 'XBt'}] |
| api-v1-user-wallet.snapshot-all.csv | amount | 15 | 0.0 | 11000120000.0 | 9910316457.9 | [{'absolute_value': 11000120000.0, 'line': 4, 'value': 11000120000.0, 'timestamp': '2026-04-29T02:09:35.360Z', 'currency': 'BMEx'}, {'absolute_value': 3215808985.0, 'line': 2, 'value': 3215808985.0, 'timestamp': '2026-07-19T12:00:00.330Z', 'currency': 'XBt'}, {'absolute_value': 888237518.0, 'line': 3, 'value': 888237518.0, 'timestamp': '2026-05-30T00:01:00.000Z', 'currency': 'USDt'}] |
| api-v1-user-margin.snapshot-all.csv | walletBalance | 3 | 888237518.0 | 11000120000.0 | 10844433779.7 | [{'absolute_value': 11000120000.0, 'line': 2, 'value': 11000120000.0, 'timestamp': '2026-04-29T02:09:35.360Z', 'currency': 'BMEx'}, {'absolute_value': 3215808985.0, 'line': 4, 'value': 3215808985.0, 'timestamp': '2026-07-19T12:35:00.504Z', 'currency': 'XBt'}, {'absolute_value': 888237518.0, 'line': 3, 'value': 888237518.0, 'timestamp': '2026-05-30T00:01:00.000Z', 'currency': 'USDt'}] |
| api-v1-user-margin.snapshot-all.csv | marginBalance | 3 | 888237518.0 | 11000120000.0 | 10847732883.08 | [{'absolute_value': 11000120000.0, 'line': 2, 'value': 11000120000.0, 'timestamp': '2026-04-29T02:09:35.360Z', 'currency': 'BMEx'}, {'absolute_value': 3380764154.0, 'line': 4, 'value': 3380764154.0, 'timestamp': '2026-07-19T12:35:00.504Z', 'currency': 'XBt'}, {'absolute_value': 888237518.0, 'line': 3, 'value': 888237518.0, 'timestamp': '2026-05-30T00:01:00.000Z', 'currency': 'USDt'}] |
| api-v1-user-margin.snapshot-all.csv | amount | 3 | 888237518.0 | 11000120000.0 | 10844433779.7 | [{'absolute_value': 11000120000.0, 'line': 2, 'value': 11000120000.0, 'timestamp': '2026-04-29T02:09:35.360Z', 'currency': 'BMEx'}, {'absolute_value': 3215808985.0, 'line': 4, 'value': 3215808985.0, 'timestamp': '2026-07-19T12:35:00.504Z', 'currency': 'XBt'}, {'absolute_value': 888237518.0, 'line': 3, 'value': 888237518.0, 'timestamp': '2026-05-30T00:01:00.000Z', 'currency': 'USDt'}] |
| api-v1-user-margin.snapshot-all.csv | realisedPnl | 3 | 0.0 | 0.0 | 0.0 | [{'absolute_value': 0.0, 'line': 2, 'value': 0.0, 'timestamp': '2026-04-29T02:09:35.360Z', 'currency': 'BMEx'}, {'absolute_value': 0.0, 'line': 3, 'value': 0.0, 'timestamp': '2026-05-30T00:01:00.000Z', 'currency': 'USDt'}, {'absolute_value': 0.0, 'line': 4, 'value': 0.0, 'timestamp': '2026-07-19T12:35:00.504Z', 'currency': 'XBt'}] |
| api-v1-user-walletSummary.all.csv | amount | 80 | -7346000000.0 | 18346120000.0 | 12542780000.0 | [{'absolute_value': 18346120000.0, 'line': 78, 'value': 18346120000.0, 'currency': 'BMEx', 'transactType': 'Transfer'}, {'absolute_value': 11000120000.0, 'line': 75, 'value': 11000120000.0, 'currency': 'BMEx', 'transactType': 'Total'}, {'absolute_value': 7346000000.0, 'line': 72, 'value': -7346000000.0, 'currency': 'BMEx', 'transactType': 'SpotTrade'}] |
| api-v1-user-walletSummary.all.csv | fee | 80 | -129849982.0 | 81245821.0 | 91452694.81 | [{'absolute_value': 129849982.0, 'line': 5, 'value': -129849982.0, 'currency': 'XBt', 'transactType': 'Funding'}, {'absolute_value': 81245821.0, 'line': 66, 'value': 81245821.0, 'symbol': 'XBTUSD', 'currency': 'XBt', 'transactType': 'RealisedPNL'}, {'absolute_value': 47422095.0, 'line': 77, 'value': -47422095.0, 'currency': 'XBt', 'transactType': 'Total'}] |
| api-v1-user-walletSummary.all.csv | walletBalance | 80 | -7346000000.0 | 18346120000.0 | 12542780000.0 | [{'absolute_value': 18346120000.0, 'line': 78, 'value': 18346120000.0, 'currency': 'BMEx', 'transactType': 'Transfer'}, {'absolute_value': 11000120000.0, 'line': 75, 'value': 11000120000.0, 'currency': 'BMEx', 'transactType': 'Total'}, {'absolute_value': 7346000000.0, 'line': 72, 'value': -7346000000.0, 'currency': 'BMEx', 'transactType': 'SpotTrade'}] |
| api-v1-user-walletSummary.all.csv | marginBalance | 80 | -7346000000.0 | 18346120000.0 | 12542780000.0 | [{'absolute_value': 18346120000.0, 'line': 78, 'value': 18346120000.0, 'currency': 'BMEx', 'transactType': 'Transfer'}, {'absolute_value': 11000120000.0, 'line': 75, 'value': 11000120000.0, 'currency': 'BMEx', 'transactType': 'Total'}, {'absolute_value': 7346000000.0, 'line': 72, 'value': -7346000000.0, 'currency': 'BMEx', 'transactType': 'SpotTrade'}] |
| api-v1-user-walletSummary.all.csv | realisedPnl | 80 | 0.0 | 0.0 | 0.0 | [{'absolute_value': 0.0, 'line': 72, 'value': 0.0, 'currency': 'BMEx', 'transactType': 'SpotTrade'}, {'absolute_value': 0.0, 'line': 73, 'value': 0.0, 'currency': 'USDt', 'transactType': 'SpotTrade'}, {'absolute_value': 0.0, 'line': 76, 'value': 0.0, 'currency': 'USDt', 'transactType': 'Total'}] |

### walletBalance 跳变候选（按原始单位的绝对变化排序）

| 币种 | 时间 | 类型 | 前余额 | 当前余额 | 变化 | 相对变化 |
| --- | --- | --- | --- | --- | --- | --- |
| USDt | 2022-02-22T16:48:51.639Z | Conversion | 170380300000.0 | 70380300000.0 | -100000000000.0 | -0.586922314375547 |
| USDt | 2022-02-22T16:48:29.806Z | Conversion | 270380300000.0 | 170380300000.0 | -100000000000.0 | -0.3698494305983091 |
| USDt | 2022-02-22T16:48:10.411Z | Conversion | 370380300000.0 | 270380300000.0 | -100000000000.0 | -0.26999276149406437 |
| USDt | 2022-02-22T16:47:58.175Z | Conversion | 470380300000.0 | 370380300000.0 | -100000000000.0 | -0.2125939372886152 |
| USDt | 2022-02-22T12:22:24.852Z | Conversion | 74983620000.0 | 149952440000.0 | 74968820000.0 | 0.9998026235596521 |
| USDt | 2022-02-22T12:22:39.954Z | Conversion | 149952440000.0 | 224887780000.0 | 74935340000.0 | 0.4997273802280243 |
| USDt | 2022-02-22T12:22:58.634Z | Conversion | 224887780000.0 | 299797600000.0 | 74909820000.0 | 0.33309866814461864 |
| USDt | 2022-02-22T12:23:15.883Z | Conversion | 299797600000.0 | 374608780000.0 | 74811180000.0 | 0.24953895561538852 |
| USDt | 2022-02-22T12:23:35.19Z | Conversion | 374608780000.0 | 449377620000.0 | 74768840000.0 | 0.19959179814205102 |
| USDt | 2022-02-22T16:49:01.177Z | Conversion | 70380300000.0 | 0.0 | -70380300000.0 | -1.0 |
| USDt | 2022-02-22T12:23:45.475Z | Conversion | 449377620000.0 | 470380300000.0 | 21002680000.0 | 0.04673726297273104 |
| BMEx | 2025-12-01T11:57:33.42Z | Transfer | 120000.0 | 11000120000.0 | 11000000000.0 | 91666.66666666667 |
| BMEx | 2023-08-31T18:02:42.143Z | SpotTrade | 12946120000.0 | 5119120000.0 | -7827000000.0 | -0.6045826857776693 |
| BMEx | 2022-12-13T07:10:43.684Z | SpotTrade | 10697120000.0 | 3164120000.0 | -7533000000.0 | -0.7042082354876826 |
| USDt | 2022-12-13T07:10:43.684Z | SpotTrade | 1004892000.0 | 5603623000.0 | 4598731000.0 | 4.5763435274636475 |
| USDt | 2023-10-23T20:26:14.841Z | SpotTrade | 4562039227.0 | 14538560.0 | -4547500667.0 | -0.9968131444565503 |
| BMEx | 2022-12-02T22:45:44.069Z | SpotTrade | 10322120000.0 | 6844120000.0 | -3478000000.0 | -0.3369462862280229 |
| XBt | 2022-01-31T13:03:53.033Z | Withdrawal | 6260107657.0 | 3260087657.0 | -3000020000.0 | -0.4792281801488514 |
| BMEx | 2023-02-13T14:41:39.689Z | SpotTrade | 6174120000.0 | 9101120000.0 | 2927000000.0 | 0.47407565774555727 |
| USDt | 2023-08-31T18:02:42.143Z | SpotTrade | 108000.0 | 2759700755.0 | 2759592755.0 | 25551.78476851852 |

## BitMEX 单位风险

Do not treat all numeric fields as BTC. Wallet ledger quantities use currency-specific asset scale; contract quantities are contracts; price/notional/PnL/fee fields require instrument, currency, and settlement metadata.

### wallet-assets scale 观测

| currency | majorCurrency | scale | 类型 | 保证金币种 |
| --- | --- | --- | --- | --- |
| AAVe | AAVE | 8 | Crypto | false |
| ADa | ADA | 8 | Crypto | false |
| APe | APE | 8 | Crypto | false |
| ATOm | ATOM | 6 | Crypto | false |
| AVAx | AVAX | 8 | Crypto | false |
| AXs | AXS | 8 | Crypto | false |
| BCh | BCH | 8 | Crypto | false |
| BMEx | BMEX | 6 | Crypto | false |
| BNb | BNB | 8 | Crypto | false |
| BONk | BONK | 5 | Crypto | false |
| BUSd | BUSD | 6 | Crypto | false |
| CRo | CRO | 6 | Crypto | false |
| DAi | DAI | 6 | Crypto | false |
| DOGe | DOGE | 6 | Crypto | false |
| DOt | DOT | 8 | Crypto | false |
| FTm | FTM | 8 | Crypto | false |
| FTr | FTR | 5 | Crypto | false |
| FTt | FTT | 8 | Crypto | false |
| GATa | GATA | 8 | Crypto | false |
| GOAt | GOAT | 8 | Crypto | false |
| Gwei | ETH | 9 | Crypto | false |
| HYPe | HYPE | 8 | Crypto | false |
| KAMa | KAMA | 5 | Crypto | false |
| LAMp | SOL | 9 | Crypto | false |
| LINk | LINK | 8 | Crypto | false |
| LOt | LOT | 5 | Crypto | false |
| LTc | LTC | 8 | Crypto | false |
| MAMUSd | MAMUSD | 6 | Synthetic | false |
| MANa | MANA | 8 | Crypto | false |
| MATIc | MATIC | 8 | Crypto | false |
| NEAr | NEAR | 8 | Crypto | false |
| OKb | OKB | 8 | Crypto | false |
| POl | POL | 9 | Crypto | false |
| RLUSd | RLUSD | 6 | Crypto | false |
| SANd | SAND | 8 | Crypto | false |
| SHIb | SHIB | 5 | Crypto | false |
| STLs | STLS | 8 | Crypto | false |
| SUSHi | SUSHI | 8 | Crypto | false |
| TAXTRUMp | TAXTRUMP | 8 | Crypto | false |
| TRUMp | TRUMP | 8 | Crypto | false |
| TRx | TRX | 6 | Crypto | false |
| UNi | UNI | 8 | Crypto | false |
| USDc | USDC | 6 | Crypto | false |
| USDe | USDE | 6 | Crypto | false |
| USDt | USDT | 6 | Crypto | true |
| WBTc | WBTC | 8 | Crypto | false |
| XAUt | XAUT | 6 | Crypto | false |
| XBt | XBT | 8 | Crypto | true |
| XRp | XRP | 6 | Crypto | false |
| XTz | XTZ | 8 | Crypto | false |
| fjUSDt | fjUSDT | 6 | Crypto | false |
| s | S | 8 | Crypto | false |

需要后续标准化的字段：

- 钱包历史与 wallet/margin snapshot 的 `amount`、`fee`、`walletBalance`、`marginBalance`：按 `currency` 查 `wallet-assets.scale`。
- 成交表的 `execCost`、`execComm`、`realisedPnl`、`homeNotional`、`foreignNotional`：结合 `currency`、`settlCurrency`、`symbol` 对照 instrument 元数据。
- 订单/成交的 `orderQty`、`lastQty`、`cumQty`、`leavesQty`、`displayQty`：合约数量，不应直接当 BTC 金额。
- `price`、`lastPx`、`avgPx`、`stopPx`：报价价格；需按 instrument 的 quote/settle 语义解释。
- `derived-equity-curve.csv`：已是派生的 XBT 等值曲线，必须按其 methodology 使用，不能当作原始钱包账本。

## 阻塞后续仓位重建的问题

当前没有达到审计规则阈值的硬阻塞项。

注意事项：

- 1 of 31717 unique execution orderIDs (0.0032%) do not match the order ledger; inspect before trusting order intent.
- Exact duplicate rows exist in at least one table; they are reported, not removed.
- Wallet, PnL, fee, notional, quantity, and price fields still require BitMEX unit normalization before PnL/equity reconstruction.
- Wallet balance jump candidates require event-type and asset-scale interpretation; this audit does not auto-repair or explain them.

## M0-02 建议

- Use execution timestamp as the event stream and retain transactTime as a secondary audit field.
- Replay every Trade row in timestamp/order-preserving order; do not deduplicate repeated orderID lifecycle rows.
- Join instrument metadata by symbol and apply currency-specific asset scales before aggregating PnL, fees, costs, and balances.
- Use terminal position, wallet, and margin snapshots as reconciliation anchors after replay.
- Investigate unmatched execution orderIDs and wallet balance jump candidates before treating intent or equity as complete.

## 机器可读输出

完整结构化结果见同目录的 `data_audit.json`。
