# M0-01 数据集审计

本目录只做数据版本固定和数据体检，不训练模型、不接交易所 API、不修改原始 CSV/JSON、不做仓位重建或自动交易。

## 运行

在仓库根目录执行：

```bash
python quant/scripts/audit_dataset.py
```

脚本会以批量/流式方式读取 CSV，并生成：

- `quant/reports/data_audit.md`
- `quant/reports/data_audit.json`

运行测试：

```bash
pytest quant/tests -v
```

## 审计范围

- 校验 `manifest.json` 声明的文件、大小、SHA256、行数、列名和时间范围。
- 审计主要订单、成交和钱包历史表的行数、字段、缺失值、重复行、时间解析/顺序、主键质量和枚举值。
- 检查订单—成交 `orderID` 覆盖率，以及重复 `orderID` 是精确重复还是更像订单生命周期记录。
- 报告价格、数量、成交价缺失、PnL/费用/成本极端值和钱包余额跳变候选。
- 使用 instrument 和 wallet-assets 作为单位解释上下文；不会把所有数字默认当成 BTC。

所有异常只报告、不自动修复。原始数据文件应保持不变。
