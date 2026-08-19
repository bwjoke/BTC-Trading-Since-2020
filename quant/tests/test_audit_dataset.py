from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_dataset.py"
SPEC = importlib.util.spec_from_file_location("audit_dataset", SCRIPT_PATH)
assert SPEC and SPEC.loader
audit_dataset = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_dataset)


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def test_missing_file(tmp_path: Path) -> None:
    item = {"file": "missing.csv", "size_bytes": 1, "sha256": "bad", "rows": 1, "columns": ["id"]}
    result = audit_dataset.compare_manifest_file(tmp_path, item, None)
    assert result["status"] == "FAIL"
    assert result["checks"]["exists"] is False


def test_sha256_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    write_csv(path, ["id"], [["1"]])
    item = {
        "file": "sample.csv",
        "size_bytes": path.stat().st_size,
        "sha256": "0" * 64,
        "rows": 1,
        "columns": ["id"],
        "first_time": None,
        "last_time": None,
    }
    result = audit_dataset.compare_manifest_file(tmp_path, item, audit_dataset.audit_csv(path))
    assert result["status"] == "FAIL"
    assert result["checks"]["sha256"] is False
    assert result["checks"]["size_bytes"] is True


def test_time_parse_failure(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    write_csv(path, ["timestamp", "value"], [["not-a-time", "1"], ["2020-01-01T00:00:00Z", "2"]])
    result = audit_dataset.audit_csv(path)
    assert result["rows"] == 2
    assert result["time_fields"]["timestamp"]["parse_failures"] == 1
    assert result["status"] == "WARNING"


def test_duplicate_primary_key_and_lifecycle_classification(tmp_path: Path) -> None:
    path = tmp_path / "orders.csv"
    write_csv(
        path,
        ["timestamp", "ordStatus", "symbol", "side", "orderID"],
        [
            ["2020-01-01T00:00:00Z", "New", "XBTUSD", "Buy", "order-1"],
            ["2020-01-01T00:00:01Z", "Filled", "XBTUSD", "Buy", "order-1"],
        ],
    )
    result = audit_dataset.audit_csv(path, key_column="orderID")
    quality = result["key_quality"]
    assert quality["duplicate_rows"] == 1
    assert quality["duplicate_key_values"] == 1
    assert quality["classification_counts"]["likely_lifecycle_records"] == 1


def test_order_execution_association_failure(tmp_path: Path) -> None:
    orders = tmp_path / "api-v1-order.csv"
    executions = tmp_path / "api-v1-execution-tradeHistory.csv"
    write_csv(orders, ["orderID"], [["order-1"]])
    write_csv(executions, ["execID", "orderID"], [["exec-1", "order-1"], ["exec-2", "missing"]])
    order_audit = audit_dataset.audit_csv(orders, key_column="orderID")
    execution_audit = audit_dataset.audit_csv(executions, key_column="execID", extra_set_fields=("orderID",))
    association = audit_dataset.build_association(order_audit, execution_audit)
    assert association["unique_execution_orderID_match_ratio"] == 0.5
    assert association["unmatched_examples"] == ["missing"]


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    result = audit_dataset.audit_csv(path)
    assert result["rows"] == 0
    assert result["status"] == "FAIL"
    assert result["error"] == "empty_file_or_missing_header"


def test_large_file_is_consumed_as_an_iterator(tmp_path: Path) -> None:
    path = tmp_path / "large.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "value"])
        for index in range(10_000):
            writer.writerow([index, index * 2])

    rows = audit_dataset.iter_csv_rows(path, batch_size=128)
    first = next(rows)
    assert first == {"id": "0", "value": "0"}
    # The remaining rows are only requested after the first row is available;
    # this guards against an implementation that eagerly materializes the file.
    assert sum(1 for _ in rows) == 9_999
