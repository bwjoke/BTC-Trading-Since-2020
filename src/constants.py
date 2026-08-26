"""路径常量与 BitMEX 合约规格缓存。"""

from pathlib import Path

# ── 数据目录 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT

# 原始数据文件
TRADE_HISTORY_CSV = DATA_DIR / "api-v1-execution-tradeHistory.csv"
ORDER_CSV = DATA_DIR / "api-v1-order.csv"
WALLET_HISTORY_CSV = DATA_DIR / "api-v1-user-walletHistory.csv"
POSITION_SNAPSHOT_CSV = DATA_DIR / "api-v1-position.snapshot.csv"
WALLET_SNAPSHOT_CSV = DATA_DIR / "api-v1-user-wallet.snapshot-all.csv"
MARGIN_SNAPSHOT_CSV = DATA_DIR / "api-v1-user-margin.snapshot-all.csv"
INSTRUMENT_CSV = DATA_DIR / "api-v1-instrument.all.csv"
WALLET_ASSETS_CSV = DATA_DIR / "api-v1-wallet-assets.csv"
WALLET_SUMMARY_CSV = DATA_DIR / "api-v1-user-walletSummary.all.csv"
EQUITY_CURVE_CSV = DATA_DIR / "derived-equity-curve.csv"
MANIFEST_JSON = DATA_DIR / "manifest.json"

# ── BitMEX 单位换算 ──────────────────────────────────────
XBT_TO_SATOSHI = 100_000_000
XBt_TO_XBT = 1_000_000  # 1 XBT = 1,000,000 XBt（BitMEX 内部单位）

# ── 输出目录 ──────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── manifest 行数校验基准 ─────────────────────────────────
MANIFEST_ROW_COUNTS = {
    "api-v1-execution-tradeHistory.csv": 173434,
    "api-v1-order.csv": 43251,
    "api-v1-user-walletHistory.csv": 17484,
    "api-v1-position.snapshot.csv": 1,
    "api-v1-user-wallet.snapshot-all.csv": 15,
    "api-v1-user-margin.snapshot-all.csv": 3,
    "api-v1-instrument.all.csv": 3090,
    "api-v1-wallet-assets.csv": 52,
    "api-v1-user-walletSummary.all.csv": 80,
    "derived-equity-curve.csv": 17468,
}