#!/usr/bin/env python3
"""M0-01 dataset audit for the public BitMEX trading archive.

The audit is deliberately read-only.  CSV files are consumed in batches when
Polars is available and otherwise through Python's streaming csv reader.  The
script never writes back to a source CSV/JSON file; it only writes the two
reports under quant/reports.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import math
import os
import statistics
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "manifest.json"
DEFAULT_REPORT_DIR = ROOT / "quant" / "reports"
BATCH_SIZE = 50_000

PRIMARY_FILES = {
    "api-v1-order.csv",
    "api-v1-execution-tradeHistory.csv",
    "api-v1-user-walletHistory.csv",
}

ENUM_FIELDS = {
    "api-v1-order.csv": ["ordStatus", "ordType", "side", "symbol"],
    "api-v1-execution-tradeHistory.csv": [
        "execType",
        "ordStatus",
        "side",
        "symbol",
        "lastLiquidityInd",
    ],
    "api-v1-user-walletHistory.csv": [
        "transactType",
        "transactStatus",
        "currency",
    ],
}

KEY_COLUMNS = {
    "api-v1-order.csv": "orderID",
    "api-v1-execution-tradeHistory.csv": "execID",
    "api-v1-user-walletHistory.csv": "transactID",
}

TIME_NAME_EXACT = {
    "timestamp",
    "transacttime",
    "listing",
    "expiry",
    "settle",
    "closingtimestamp",
    "openingtimestamp",
    "fundingtimestamp",
    "publishtime",
    "rebalancetimestamp",
}

PRICE_COLUMNS = {"price", "lastPx", "avgPx", "stopPx"}
QUANTITY_COLUMNS = {"orderQty", "lastQty", "leavesQty", "cumQty", "displayQty"}
SELECTED_NUMERIC_COLUMNS = {
    "realisedPnl",
    "execComm",
    "execCost",
    "amount",
    "fee",
    "walletBalance",
    "marginBalance",
}


def is_missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def clean_value(value: Any) -> str:
    return "" if value is None else str(value)


def parse_number(value: Any) -> float | None:
    if is_missing(value):
        return None
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def parse_time(value: Any) -> datetime | None:
    if is_missing(value):
        return None
    raw = str(value).strip()
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError, OverflowError):
        return None


def iso_time(value: datetime | None) -> str | None:
    if value is None:
        return None
    normalized = value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if "." in normalized:
        prefix, fraction = normalized[:-1].split(".", 1)
        normalized_fraction = fraction.rstrip("0")
        normalized = f"{prefix}.{normalized_fraction}Z" if normalized_fraction else f"{prefix}Z"
    return normalized


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return [column.strip() for column in next(reader)]
        except StopIteration:
            return []


def _iter_csv_stdlib(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return
        for row in reader:
            yield {key: clean_value(value) for key, value in row.items() if key is not None}


def _iter_csv_polars(path: Path, batch_size: int) -> Iterator[dict[str, str]]:
    import polars as pl  # type: ignore

    header = read_csv_header(path)
    if not header:
        return
    reader = pl.read_csv_batched(
        str(path),
        has_header=True,
        batch_size=batch_size,
        infer_schema_length=0,
        schema_overrides={column: pl.String for column in header},
    )
    while True:
        batches = reader.next_batches(1)
        if not batches:
            break
        for frame in batches:
            for row in frame.iter_rows(named=True):
                yield {column: clean_value(row.get(column)) for column in header}


def iter_csv_rows(path: Path, batch_size: int = BATCH_SIZE) -> Iterator[dict[str, str]]:
    """Yield rows without loading an entire CSV into memory.

    Polars is the preferred batch reader.  The stdlib reader is a deterministic
    fallback so the audit remains runnable in a fresh Python environment and
    tests can exercise the streaming path without a native dependency.
    """

    try:
        import polars  # noqa: F401  # type: ignore
    except ImportError:
        yield from _iter_csv_stdlib(path)
        return

    try:
        yield from _iter_csv_polars(path, batch_size)
    except Exception:
        # A malformed CSV should still produce a useful audit record.  The
        # stdlib parser is more permissive for diagnostics; parsing errors are
        # surfaced by row/column checks rather than hidden as a clean pass.
        yield from _iter_csv_stdlib(path)


def is_time_field(column: str) -> bool:
    lowered = column.lower()
    return lowered in TIME_NAME_EXACT or lowered.endswith("timestamp") or lowered.endswith("time")


def row_fingerprint(row: dict[str, str], columns: list[str]) -> str:
    encoded = json.dumps(
        [clean_value(row.get(column, "")) for column in columns],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha1(encoded).hexdigest()


def _new_numeric_stats() -> dict[str, Any]:
    return {
        "count": 0,
        "parse_failures": 0,
        "min": None,
        "max": None,
        "mean": None,
        "top_absolute_values": [],
        "_values_for_percentile": [],
    }


def _update_numeric_stats(
    stats: dict[str, Any],
    value: float | None,
    raw: Any,
    line_number: int,
    context: dict[str, Any],
) -> None:
    if is_missing(raw):
        return
    if value is None:
        stats["parse_failures"] += 1
        return
    stats["count"] += 1
    stats["min"] = value if stats["min"] is None else min(stats["min"], value)
    stats["max"] = value if stats["max"] is None else max(stats["max"], value)
    values = stats["_values_for_percentile"]
    values.append(value)
    item = (abs(value), line_number, value, context)
    heap = stats["top_absolute_values"]
    if len(heap) < 10:
        heapq.heappush(heap, item)
    elif item[:3] > heap[0][:3]:
        heapq.heapreplace(heap, item)


def _finalize_numeric_stats(stats: dict[str, Any]) -> dict[str, Any]:
    values = stats.pop("_values_for_percentile", [])
    stats["mean"] = statistics.fmean(values) if values else None
    stats["p99_absolute"] = (
        statistics.quantiles([abs(value) for value in values], n=100, method="inclusive")[98]
        if len(values) >= 2
        else (abs(values[0]) if values else None)
    )
    stats["top_absolute_values"] = [
        {
            "absolute_value": item[0],
            "line": item[1],
            "value": item[2],
            **item[3],
        }
        for item in sorted(stats["top_absolute_values"], key=lambda item: item[0], reverse=True)
    ]
    return stats


def _new_time_stats() -> dict[str, Any]:
    return {
        "nonempty": 0,
        "missing": 0,
        "parse_failures": 0,
        "out_of_order_count": 0,
        "first_time": None,
        "last_time": None,
        "_previous": None,
    }


def _new_group_stats() -> dict[str, Any]:
    return {
        "count": 0,
        "unique_row_fingerprints": set(),
        "statuses": Counter(),
        "symbols": set(),
        "sides": set(),
        "first_time": None,
        "last_time": None,
        "first_line": None,
        "last_line": None,
    }


def _jsonable_group(key: str, group: dict[str, Any]) -> dict[str, Any]:
    unique_rows = len(group["unique_row_fingerprints"])
    if group["count"] == 1:
        classification = "unique"
    elif unique_rows == 1:
        classification = "exact_duplicate_rows"
    elif len(group["statuses"]) > 1 or len(group["symbols"]) > 1 or len(group["sides"]) > 1 or group["first_time"] != group["last_time"]:
        classification = "likely_lifecycle_records"
    else:
        classification = "distinct_rows_same_key_needs_review"
    return {
        "key": key,
        "count": group["count"],
        "unique_row_fingerprints": unique_rows,
        "statuses": dict(group["statuses"]),
        "symbols": sorted(group["symbols"]),
        "sides": sorted(group["sides"]),
        "first_time": group["first_time"],
        "last_time": group["last_time"],
        "first_line": group["first_line"],
        "last_line": group["last_line"],
        "classification": classification,
    }


def audit_csv(
    path: Path,
    *,
    key_column: str | None = None,
    extra_set_fields: Iterable[str] = (),
    batch_size: int = BATCH_SIZE,
) -> dict[str, Any]:
    """Audit one CSV using bounded/batch row reads.

    Internal sets are returned under underscore-prefixed keys for cross-table
    checks and removed before report serialization.
    """

    result: dict[str, Any] = {
        "file": path.name,
        "exists": path.is_file(),
        "status": "FAIL",
        "rows": 0,
        "columns": [],
        "missing_values": {},
        "blank_rows": 0,
        "duplicate_full_rows": 0,
        "key_column": key_column,
        "key_quality": None,
        "time_fields": {},
        "primary_time_field": None,
        "first_time": None,
        "last_time": None,
        "enumerations": {field: {} for field in ENUM_FIELDS.get(path.name, [])},
        "numeric": {},
        "anomalies": {
            "nonpositive_prices": {},
            "negative_quantities": {},
            "last_qty_greater_than_order_qty": 0,
            "cum_qty_greater_than_order_qty": 0,
            "negative_leaves_qty": 0,
            "quantity_without_execution_price": 0,
            "wallet_balance_jump_candidates": [],
        },
        "reader_backend": None,
    }

    if not path.is_file():
        result["error"] = "file_missing"
        return result

    columns = read_csv_header(path)
    result["columns"] = columns
    if not columns:
        result["error"] = "empty_file_or_missing_header"
        return result

    time_fields = [column for column in columns if is_time_field(column)]
    result["primary_time_field"] = "timestamp" if "timestamp" in columns else (time_fields[0] if time_fields else None)
    time_stats = {field: _new_time_stats() for field in time_fields}
    missing = Counter()
    enum_counters = {field: Counter() for field in ENUM_FIELDS.get(path.name, []) if field in columns}
    numeric_stats = {
        field: _new_numeric_stats()
        for field in columns
        if field in SELECTED_NUMERIC_COLUMNS
    }
    nonpositive_prices = Counter()
    negative_quantities = Counter()
    seen_rows: set[str] = set()
    seen_keys: set[str] = set()
    extra_sets = {field: set() for field in extra_set_fields if field in columns}
    extra_counts = {field: Counter() for field in extra_set_fields if field in columns}
    groups: dict[str, dict[str, Any]] = {}
    previous_wallet_balance: dict[str, tuple[float, datetime | None, int]] = {}
    wallet_jump_candidates: list[tuple[float, int, dict[str, Any]]] = []

    result["reader_backend"] = "polars_batched_or_stdlib_fallback"

    try:
        rows = iter_csv_rows(path, batch_size=batch_size)
        for line_number, row in enumerate(rows, start=2):
            result["rows"] += 1
            if not any(not is_missing(row.get(column, "")) for column in columns):
                result["blank_rows"] += 1

            for column in columns:
                if is_missing(row.get(column, "")):
                    missing[column] += 1

            fingerprint = row_fingerprint(row, columns)
            if fingerprint in seen_rows:
                result["duplicate_full_rows"] += 1
            else:
                seen_rows.add(fingerprint)

            for field, counter in enum_counters.items():
                value = clean_value(row.get(field, "")).strip()
                counter[value if value else "<MISSING>"] += 1

            for field in time_fields:
                raw_time = row.get(field, "")
                stats = time_stats[field]
                parsed_time = parse_time(raw_time)
                if is_missing(raw_time):
                    stats["missing"] += 1
                else:
                    stats["nonempty"] += 1
                    if parsed_time is None:
                        stats["parse_failures"] += 1
                    else:
                        if stats["_previous"] is not None and parsed_time < stats["_previous"]:
                            stats["out_of_order_count"] += 1
                        stats["_previous"] = parsed_time
                        if stats["first_time"] is None or parsed_time < parse_time(stats["first_time"]):
                            stats["first_time"] = iso_time(parsed_time)
                        if stats["last_time"] is None or parsed_time > parse_time(stats["last_time"]):
                            stats["last_time"] = iso_time(parsed_time)

            context = {
                field: clean_value(row.get(field, ""))
                for field in ("timestamp", "symbol", "currency", "transactType", "orderID", "execID", "transactID")
                if field in columns and not is_missing(row.get(field, ""))
            }
            for field, stats in numeric_stats.items():
                raw = row.get(field, "")
                _update_numeric_stats(stats, parse_number(raw), raw, line_number, context)

            for field in PRICE_COLUMNS.intersection(columns):
                value = parse_number(row.get(field, ""))
                if value is not None and value <= 0:
                    nonpositive_prices[field] += 1
            for field in QUANTITY_COLUMNS.intersection(columns):
                value = parse_number(row.get(field, ""))
                if value is not None and value < 0:
                    negative_quantities[field] += 1

            order_qty = parse_number(row.get("orderQty", ""))
            last_qty = parse_number(row.get("lastQty", ""))
            cum_qty = parse_number(row.get("cumQty", ""))
            leaves_qty = parse_number(row.get("leavesQty", ""))
            if order_qty is not None and last_qty is not None and last_qty > order_qty:
                result["anomalies"]["last_qty_greater_than_order_qty"] += 1
            if order_qty is not None and cum_qty is not None and cum_qty > order_qty:
                result["anomalies"]["cum_qty_greater_than_order_qty"] += 1
            if leaves_qty is not None and leaves_qty < 0:
                result["anomalies"]["negative_leaves_qty"] += 1
            if path.name == "api-v1-execution-tradeHistory.csv" and last_qty is not None and last_qty > 0:
                if parse_number(row.get("lastPx", "")) is None:
                    result["anomalies"]["quantity_without_execution_price"] += 1

            if key_column and key_column in columns:
                key = clean_value(row.get(key_column, "")).strip()
                if key:
                    seen_keys.add(key)
                    group = groups.setdefault(key, _new_group_stats())
                    group["count"] += 1
                    group["unique_row_fingerprints"].add(fingerprint)
                    status = clean_value(row.get("ordStatus", "")).strip()
                    if status:
                        group["statuses"][status] += 1
                    symbol = clean_value(row.get("symbol", "")).strip()
                    side = clean_value(row.get("side", "")).strip()
                    if symbol:
                        group["symbols"].add(symbol)
                    if side:
                        group["sides"].add(side)
                    group_time = parse_time(row.get(result["primary_time_field"], "")) if result["primary_time_field"] else None
                    group_time_iso = iso_time(group_time)
                    if group["first_time"] is None or (group_time and parse_time(group["first_time"]) and group_time < parse_time(group["first_time"])):
                        group["first_time"] = group_time_iso
                    if group["last_time"] is None or (group_time and parse_time(group["last_time"]) and group_time > parse_time(group["last_time"])):
                        group["last_time"] = group_time_iso
                    group["first_line"] = group["first_line"] or line_number
                    group["last_line"] = line_number

            for field, values in extra_sets.items():
                value = clean_value(row.get(field, "")).strip()
                if value:
                    values.add(value)
                    extra_counts[field][value] += 1

            if path.name == "api-v1-user-walletHistory.csv":
                currency = clean_value(row.get("currency", "")).strip() or "<MISSING>"
                balance = parse_number(row.get("walletBalance", ""))
                event_time = parse_time(row.get("timestamp", ""))
                if balance is not None:
                    previous = previous_wallet_balance.get(currency)
                    if previous is not None:
                        delta = balance - previous[0]
                        ratio = (delta / previous[0]) if previous[0] else None
                        jump = {
                            "currency": currency,
                            "line": line_number,
                            "previous_line": previous[2],
                            "previous_balance_raw": previous[0],
                            "current_balance_raw": balance,
                            "delta_raw": delta,
                            "relative_change": ratio,
                            "timestamp": iso_time(event_time),
                            "transactType": clean_value(row.get("transactType", "")),
                            "transactStatus": clean_value(row.get("transactStatus", "")),
                        }
                        item = (abs(delta), line_number, jump)
                        if len(wallet_jump_candidates) < 20:
                            heapq.heappush(wallet_jump_candidates, item)
                        elif abs(delta) > wallet_jump_candidates[0][0]:
                            heapq.heapreplace(wallet_jump_candidates, item)
                    previous_wallet_balance[currency] = (balance, event_time, line_number)
    except Exception as exc:  # pragma: no cover - defensive guard for real exports
        result["error"] = f"row_read_error: {type(exc).__name__}: {exc}"
        return result

    result["missing_values"] = {
        column: {"count": count, "ratio": (count / result["rows"] if result["rows"] else None)}
        for column, count in sorted(missing.items())
    }
    result["time_fields"] = {}
    for field, stats in time_stats.items():
        stats.pop("_previous", None)
        result["time_fields"][field] = stats
    primary_time = result["primary_time_field"]
    if primary_time and primary_time in result["time_fields"]:
        result["first_time"] = result["time_fields"][primary_time]["first_time"]
        result["last_time"] = result["time_fields"][primary_time]["last_time"]
    result["enumerations"] = {field: dict(sorted(counter.items())) for field, counter in enum_counters.items()}
    result["numeric"] = {field: _finalize_numeric_stats(stats) for field, stats in numeric_stats.items()}
    result["anomalies"]["nonpositive_prices"] = dict(nonpositive_prices)
    result["anomalies"]["negative_quantities"] = dict(negative_quantities)
    result["anomalies"]["wallet_balance_jump_candidates"] = [
        item[2] for item in sorted(wallet_jump_candidates, key=lambda item: item[0], reverse=True)
    ]

    if key_column:
        duplicate_groups = [_jsonable_group(key, group) for key, group in groups.items() if group["count"] > 1]
        classifications = Counter(group["classification"] for group in duplicate_groups)
        result["key_quality"] = {
            "column": key_column,
            "nonempty_values": len(seen_keys),
            "missing_values": result["missing_values"].get(key_column, {}).get("count", 0),
            "duplicate_rows": sum(group["count"] - 1 for group in duplicate_groups),
            "duplicate_key_values": len(duplicate_groups),
            "classification_counts": dict(classifications),
            "duplicate_groups": sorted(duplicate_groups, key=lambda group: (-group["count"], group["key"]))[:200],
        }

    result["_value_sets"] = {key_column: seen_keys} if key_column else {}
    result["_value_sets"].update(extra_sets)
    result["_value_counts"] = extra_counts
    result["status"] = "WARNING" if (
        result["duplicate_full_rows"]
        or any(stats["parse_failures"] or stats["out_of_order_count"] for stats in result["time_fields"].values())
        or any(value["count"] for value in result["missing_values"].values())
    ) else "PASS"
    return result


def _strip_internal(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_internal(item) for key, item in value.items() if not key.startswith("_")}
    if isinstance(value, list):
        return [_strip_internal(item) for item in value]
    if isinstance(value, set):
        return sorted(value)
    return value


def time_values_equal(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    parsed_left = parse_time(left)
    parsed_right = parse_time(right)
    if parsed_left is not None and parsed_right is not None:
        return parsed_left == parsed_right
    return str(left) == str(right)


def git_blob_sha256(root: Path, relative: str) -> str | None:
    """Return the SHA256 of the committed blob, if this is a Git worktree."""

    try:
        completed = subprocess.run(
            ["git", "cat-file", "blob", f"HEAD:{relative}"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return hashlib.sha256(completed.stdout).hexdigest()


def compare_manifest_file(root: Path, item: dict[str, Any], csv_audit: dict[str, Any] | None) -> dict[str, Any]:
    relative = str(item["file"])
    path = root / relative
    check: dict[str, Any] = {
        "file": relative,
        "declared": {key: item.get(key) for key in ("rows", "columns", "sha256", "size_bytes", "first_time", "last_time") if key in item},
        "actual": {},
        "checks": {},
        "status": "FAIL",
    }
    if not path.is_file():
        check["checks"]["exists"] = False
        check["status"] = "FAIL"
        return check

    check["checks"]["exists"] = True
    actual_size = path.stat().st_size
    actual_hash = sha256_file(path)
    check["actual"].update({"size_bytes": actual_size, "sha256": actual_hash})
    check["checks"]["size_bytes"] = actual_size == item.get("size_bytes")
    check["checks"]["sha256"] = actual_hash == item.get("sha256")

    if csv_audit is not None:
        check["actual"].update(
            {
                "rows": csv_audit["rows"],
                "columns": csv_audit["columns"],
                "first_time": csv_audit["first_time"],
                "last_time": csv_audit["last_time"],
            }
        )
        check["checks"]["rows"] = csv_audit["rows"] == item.get("rows")
        check["checks"]["columns"] = csv_audit["columns"] == item.get("columns")
        check["checks"]["first_time"] = time_values_equal(csv_audit["first_time"], item.get("first_time"))
        check["checks"]["last_time"] = time_values_equal(csv_audit["last_time"], item.get("last_time"))
    else:
        check["actual"]["bytes_only"] = True

    failed_checks = [key for key, passed in check["checks"].items() if passed is False]
    if failed_checks and path.suffix.lower() in {".md", ".txt"}:
        committed_hash = git_blob_sha256(root, relative)
        if committed_hash == item.get("sha256"):
            check["status"] = "WARNING"
            check["note"] = "Committed blob matches manifest; working-tree text differs, likely due line-ending normalization."
            return check
    check["status"] = "FAIL" if failed_checks else "PASS"
    return check


def build_association(order_audit: dict[str, Any], execution_audit: dict[str, Any]) -> dict[str, Any]:
    order_ids = order_audit.get("_value_sets", {}).get("orderID", set())
    execution_order_ids = execution_audit.get("_value_sets", {}).get("orderID", set())
    execution_order_id_counts = execution_audit.get("_value_counts", {}).get("orderID", Counter())
    execution_key_quality = execution_audit.get("key_quality") or {}
    execution_order_column = execution_audit.get("missing_values", {}).get("orderID", {})
    matched_unique = execution_order_ids.intersection(order_ids)
    unmatched_unique = execution_order_ids - order_ids
    nonempty_rows = sum(execution_order_id_counts.values())
    matched_rows = sum(count for key, count in execution_order_id_counts.items() if key in order_ids)
    return {
        "execution_rows": execution_audit.get("rows", 0),
        "execution_orderID_nonempty_rows": nonempty_rows,
        "execution_orderID_missing_rows": execution_order_column.get("count", 0),
        "execution_orderID_nonempty_ratio": nonempty_rows / execution_audit.get("rows", 0) if execution_audit.get("rows", 0) else None,
        "unique_execution_orderIDs": len(execution_order_ids),
        "unique_orderIDs": len(order_ids),
        "unique_execution_orderIDs_matched": len(matched_unique),
        "unique_execution_orderIDs_unmatched": len(unmatched_unique),
        "unique_execution_orderID_match_ratio": len(matched_unique) / len(execution_order_ids) if execution_order_ids else None,
        "matched_execution_orderID_rows": matched_rows,
        "row_level_match_ratio": matched_rows / nonempty_rows if nonempty_rows else None,
        "unmatched_examples": sorted(unmatched_unique)[:50],
        "note": "Unique-ID coverage is reported separately from row-level coverage because an execution orderID can appear on many fill rows.",
        "execution_key_duplicate_rows": execution_key_quality.get("duplicate_rows", 0),
    }


def load_wallet_asset_scales(root: Path) -> dict[str, Any]:
    path = root / "api-v1-wallet-assets.csv"
    scales: dict[str, Any] = {}
    if not path.is_file():
        return scales
    for row in iter_csv_rows(path):
        currency = clean_value(row.get("currency", "")).strip()
        if not currency:
            continue
        scale = parse_number(row.get("scale", ""))
        scales[currency] = {
            "scale": int(scale) if scale is not None and scale.is_integer() else scale,
            "majorCurrency": clean_value(row.get("majorCurrency", "")),
            "name": clean_value(row.get("name", "")),
            "currencyType": clean_value(row.get("currencyType", "")),
            "isMarginCurrency": clean_value(row.get("isMarginCurrency", "")),
        }
    return scales


def load_instrument_summary(root: Path) -> dict[str, Any]:
    path = root / "api-v1-instrument.all.csv"
    if not path.is_file():
        return {"rows": 0, "symbols": [], "settlement_currencies": {}}
    symbols = set()
    settlement = Counter()
    inverse = Counter()
    for row in iter_csv_rows(path):
        symbol = clean_value(row.get("symbol", "")).strip()
        if symbol:
            symbols.add(symbol)
        currency = clean_value(row.get("settlCurrency", "")).strip() or "<MISSING>"
        settlement[currency] += 1
        inverse[clean_value(row.get("isInverse", "")).strip() or "<MISSING>"] += 1
    return {
        "rows": sum(settlement.values()),
        "unique_symbols": len(symbols),
        "settlement_currencies": dict(sorted(settlement.items())),
        "isInverse": dict(sorted(inverse.items())),
    }


def evaluate_readiness(
    manifest_checks: list[dict[str, Any]],
    audits: dict[str, dict[str, Any]],
    association: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    caveats: list[str] = []
    failed_manifest = [check["file"] for check in manifest_checks if check["status"] == "FAIL"]
    if failed_manifest:
        blockers.append(f"Manifest mismatch or missing files: {', '.join(failed_manifest)}")

    execution = audits.get("api-v1-execution-tradeHistory.csv", {})
    order = audits.get("api-v1-order.csv", {})
    wallet = audits.get("api-v1-user-walletHistory.csv", {})
    if execution.get("key_quality", {}).get("duplicate_rows", 0):
        blockers.append("execID is not unique in the execution ledger.")
    if wallet.get("key_quality", {}).get("duplicate_rows", 0):
        blockers.append("transactID is not unique in walletHistory.")
    for filename in PRIMARY_FILES:
        audit = audits.get(filename, {})
        invalid_times = sum(stats.get("parse_failures", 0) for stats in audit.get("time_fields", {}).values())
        if invalid_times:
            blockers.append(f"{filename} contains {invalid_times} unparseable non-empty time values.")
        if not audit.get("rows"):
            blockers.append(f"{filename} has no data rows.")

    ratio = association.get("unique_execution_orderID_match_ratio")
    if ratio is not None and ratio < 0.95:
        blockers.append(f"Execution-to-order unique orderID coverage is only {ratio:.2%} (<95%).")
    elif ratio is not None and ratio < 1.0:
        unmatched_count = association.get("unique_execution_orderIDs_unmatched", 0)
        total_unique = association.get("unique_execution_orderIDs", 0)
        caveats.append(f"{unmatched_count} of {total_unique} unique execution orderIDs ({1 - ratio:.4%}) do not match the order ledger; inspect before trusting order intent.")

    order_duplicates = order.get("key_quality", {}).get("classification_counts", {})
    if order_duplicates.get("likely_lifecycle_records", 0):
        caveats.append("Repeated orderID values appear to be lifecycle/state rows in at least some groups; preserve them for replay.")
    if any(audit.get("duplicate_full_rows", 0) for audit in audits.values()):
        caveats.append("Exact duplicate rows exist in at least one table; they are reported, not removed.")
    caveats.append("Wallet, PnL, fee, notional, quantity, and price fields still require BitMEX unit normalization before PnL/equity reconstruction.")
    caveats.append("Wallet balance jump candidates require event-type and asset-scale interpretation; this audit does not auto-repair or explain them.")

    if blockers:
        status = "BLOCKED"
    elif caveats:
        status = "READY_WITH_WARNINGS"
    else:
        status = "READY"
    return {"status": status, "blockers": blockers, "caveats": caveats}


def audit_dataset(root: Path = ROOT, report_dir: Path = DEFAULT_REPORT_DIR, batch_size: int = BATCH_SIZE) -> dict[str, Any]:
    manifest_path = root / "manifest.json"
    report_dir.mkdir(parents=True, exist_ok=True)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest.json not found under {root}")
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    audits: dict[str, dict[str, Any]] = {}
    manifest_checks: list[dict[str, Any]] = []
    for item in manifest.get("files", []):
        filename = str(item["file"])
        csv_audit = None
        if filename.lower().endswith(".csv"):
            csv_audit = audit_csv(
                root / filename,
                key_column=KEY_COLUMNS.get(filename),
                extra_set_fields=("orderID",) if filename == "api-v1-execution-tradeHistory.csv" else (),
                batch_size=batch_size,
            )
            audits[filename] = csv_audit
        manifest_checks.append(compare_manifest_file(root, item, csv_audit))

    order_audit = audits.get("api-v1-order.csv", {})
    execution_audit = audits.get("api-v1-execution-tradeHistory.csv", {})
    association = build_association(order_audit, execution_audit)
    unit_context = {
        "wallet_asset_scales": load_wallet_asset_scales(root),
        "instrument_summary": load_instrument_summary(root),
        "raw_unit_risk": {
            "wallet_fields": ["amount", "fee", "walletBalance", "marginBalance"],
            "execution_fields": ["execCost", "execComm", "realisedPnl", "homeNotional", "foreignNotional"],
            "order_fields": ["orderQty", "cumQty", "leavesQty", "displayQty", "price", "avgPx", "stopPx"],
            "snapshot_fields": ["amount", "walletBalance", "marginBalance", "realisedPnl", "unrealisedPnl", "markValue"],
            "interpretation": "Do not treat all numeric fields as BTC. Wallet ledger quantities use currency-specific asset scale; contract quantities are contracts; price/notional/PnL/fee fields require instrument, currency, and settlement metadata.",
        },
    }
    readiness = evaluate_readiness(manifest_checks, audits, association)

    data: dict[str, Any] = {
        "audit_version": "M0-01/1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "root": str(root),
        "source": {
            "repository": "bwjoke/BTC-Trading-Since-2020",
            "commit": _git_commit(root),
            "branch": _git_branch(root),
            "manifest_generated_at": manifest.get("generated_at"),
            "dataset_window_declared": manifest.get("dataset_window"),
        },
        "reader": {
            "mode": "Polars batched reader with stdlib csv streaming fallback",
            "batch_size": batch_size,
            "raw_files_modified": False,
        },
        "manifest_consistency": {
            "spec_version": manifest.get("spec_version"),
            "file_count": len(manifest.get("files", [])),
            "checks": manifest_checks,
            "pass_count": sum(check["status"] == "PASS" for check in manifest_checks),
            "warning_count": sum(check["status"] == "WARNING" for check in manifest_checks),
            "fail_count": sum(check["status"] == "FAIL" for check in manifest_checks),
        },
        "files": _strip_internal(audits),
        "associations": {"execution_to_order": association},
        "unit_context": unit_context,
        "readiness": readiness,
        "m0_02_suggestions": [
            "Use execution timestamp as the event stream and retain transactTime as a secondary audit field.",
            "Replay every Trade row in timestamp/order-preserving order; do not deduplicate repeated orderID lifecycle rows.",
            "Join instrument metadata by symbol and apply currency-specific asset scales before aggregating PnL, fees, costs, and balances.",
            "Use terminal position, wallet, and margin snapshots as reconciliation anchors after replay.",
            "Investigate unmatched execution orderIDs and wallet balance jump candidates before treating intent or equity as complete.",
        ],
    }

    json_path = report_dir / "data_audit.json"
    md_path = report_dir / "data_audit.md"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")
    write_markdown_report(data, md_path)
    return data


def _git_commit(root: Path) -> str | None:
    head = root / ".git" / "HEAD"
    if not head.is_file():
        return None
    raw = head.read_text(encoding="utf-8").strip()
    if raw.startswith("ref: "):
        ref = root / ".git" / raw[5:]
        if ref.is_file():
            return ref.read_text(encoding="utf-8").strip()
        packed = root / ".git" / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith("#") and " " in line:
                    commit, candidate = line.split(" ", 1)
                    if candidate == raw[6:]:
                        return commit
    return raw if len(raw) == 40 else None


def _git_branch(root: Path) -> str | None:
    head = root / ".git" / "HEAD"
    if not head.is_file():
        return None
    raw = head.read_text(encoding="utf-8").strip()
    return raw[16:] if raw.startswith("ref: refs/heads/") else None


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        text = "" if value is None else str(value)
        return text.replace("|", "\\|").replace("\n", " ")

    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    output.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def write_markdown_report(data: dict[str, Any], path: Path) -> None:
    manifest = data["manifest_consistency"]
    readiness = data["readiness"]
    files = data["files"]
    lines: list[str] = [
        "# M0-01 数据集审计报告",
        "",
        f"生成时间（UTC）：`{data['generated_at_utc']}`",
        f"数据版本 commit：`{data['source'].get('commit') or '未知'}`",
        f"分析分支：`{data['source'].get('branch') or '未知'}`",
        "",
        "## 执行摘要",
        "",
        f"- Manifest 文件检查：**{manifest['pass_count']} PASS / {manifest['warning_count']} WARNING / {manifest['fail_count']} FAIL**。",
        f"- M0-02 仓位重建判断：**{readiness['status']}**。",
        f"- 订单数：`{files.get('api-v1-order.csv', {}).get('rows', 0):,}`；成交数：`{files.get('api-v1-execution-tradeHistory.csv', {}).get('rows', 0):,}`；钱包事件数：`{files.get('api-v1-user-walletHistory.csv', {}).get('rows', 0):,}`。",
        "- 本阶段只读原始数据，未训练模型、未连接交易所、未进行自动修复。",
        "",
        "## 数据文件清单",
        "",
    ]
    file_rows = []
    for check in manifest["checks"]:
        audit = files.get(check["file"], {})
        file_rows.append([
            check["file"],
            check["status"],
            audit.get("status", "N/A"),
            check["actual"].get("rows", "N/A"),
            check["actual"].get("size_bytes", "N/A"),
        ])
    lines.append(markdown_table(["文件", "Manifest", "数据", "实际行数", "字节数"], file_rows))
    lines.extend(["", "## Manifest 一致性", "", "每个文件均按存在性、文件大小、SHA256、声明列名、声明行数和时间范围核对。"])
    manifest_rows = []
    for check in manifest["checks"]:
        failed = [key for key, passed in check["checks"].items() if not passed]
        manifest_rows.append([check["file"], check["status"], ", ".join(failed) if failed else "全部通过"])
    lines.append(markdown_table(["文件", "结果", "失败检查"], manifest_rows))

    lines.extend(["", "## 字段与行数检查", ""])
    field_rows = []
    for filename, audit in files.items():
        field_rows.append([filename, audit.get("status"), audit.get("rows"), len(audit.get("columns", [])), audit.get("first_time"), audit.get("last_time")])
    lines.append(markdown_table(["文件", "状态", "行数", "列数", "最早时间", "最晚时间"], field_rows))
    for filename in sorted(PRIMARY_FILES):
        audit = files.get(filename, {})
        lines.extend(["", f"### `{filename}` 列名", "", "```text", ",".join(audit.get("columns", [])), "```"])

    lines.extend(["", "## 时间范围与顺序", ""])
    time_rows = []
    for filename, audit in files.items():
        for field, stats in audit.get("time_fields", {}).items():
            time_rows.append([filename, field, stats.get("nonempty"), stats.get("parse_failures"), stats.get("out_of_order_count"), stats.get("first_time"), stats.get("last_time")])
    lines.append(markdown_table(["文件", "字段", "非空", "解析失败", "乱序数", "最早", "最晚"], time_rows))

    lines.extend(["", "## 主键质量", ""])
    key_rows = []
    for filename in sorted(PRIMARY_FILES):
        audit = files.get(filename, {})
        quality = audit.get("key_quality") or {}
        key_rows.append([filename, quality.get("column"), quality.get("nonempty_values"), quality.get("missing_values"), quality.get("duplicate_rows"), quality.get("duplicate_key_values"), quality.get("classification_counts")])
    lines.append(markdown_table(["文件", "主键", "非空唯一值", "空值", "重复行", "重复键值", "重复分类"], key_rows))
    lines.extend(["", "重复 `orderID` 分析：同一 `orderID` 多行不能直接视为脏数据；报告将状态、symbol、side、时间跨度不同的组标记为 `likely_lifecycle_records`，并保留其行。", ""])
    for filename in sorted(PRIMARY_FILES):
        groups = (files.get(filename, {}).get("key_quality") or {}).get("duplicate_groups", [])
        if groups:
            lines.extend([f"### `{filename}` 重复键示例（最多 200 组）", "", markdown_table(["键", "行数", "状态", "时间范围", "分类", "首末行"], [[group["key"], group["count"], group["statuses"], f"{group['first_time']} → {group['last_time']}", group["classification"], f"{group['first_line']} → {group['last_line']}"] for group in groups])])

    lines.extend(["", "## 表关联覆盖率", ""])
    assoc = data["associations"]["execution_to_order"]
    lines.append(markdown_table(["指标", "值"], [
        ["成交行数", assoc.get("execution_rows")],
        ["成交 orderID 非空行数", assoc.get("execution_orderID_nonempty_rows")],
        ["成交 orderID 空值行数", assoc.get("execution_orderID_missing_rows")],
        ["成交 orderID 非空比例", f"{assoc['execution_orderID_nonempty_ratio']:.4%}" if assoc.get("execution_orderID_nonempty_ratio") is not None else "N/A"],
        ["按非空成交行的 orderID 关联率", f"{assoc['row_level_match_ratio']:.4%}" if assoc.get("row_level_match_ratio") is not None else "N/A"],
        ["订单表唯一 orderID", assoc.get("unique_orderIDs")],
        ["成交表唯一 orderID", assoc.get("unique_execution_orderIDs")],
        ["成交 orderID 匹配唯一值", assoc.get("unique_execution_orderIDs_matched")],
        ["成交 orderID 未匹配唯一值", assoc.get("unique_execution_orderIDs_unmatched")],
        ["唯一 orderID 关联率", f"{assoc['unique_execution_orderID_match_ratio']:.4%}" if assoc.get("unique_execution_orderID_match_ratio") is not None else "N/A"],
    ]))
    if assoc.get("unmatched_examples"):
        lines.extend(["", "未匹配 orderID 示例：", "", "```text", "\n".join(assoc["unmatched_examples"]), "```"])

    lines.extend(["", "## 缺失值", "", "以下列出每个文件的非零缺失列；比例按该文件数据行数计算。"])
    missing_rows = []
    for filename, audit in files.items():
        for column, stats in audit.get("missing_values", {}).items():
            if stats.get("count", 0):
                missing_rows.append([filename, column, stats["count"], f"{stats['ratio']:.4%}"])
    lines.append(markdown_table(["文件", "字段", "缺失数", "缺失比例"], missing_rows or [["全部文件", "无非零缺失", 0, "0%"]]))

    lines.extend(["", "## 重复数据", ""])
    duplicate_rows = [[filename, audit.get("rows"), audit.get("duplicate_full_rows"), (audit.get("key_quality") or {}).get("duplicate_rows", "N/A")] for filename, audit in files.items()]
    lines.append(markdown_table(["文件", "行数", "完全重复行（首行后）", "主键重复行"], duplicate_rows))

    lines.extend(["", "## 枚举值分布", ""])
    for filename in sorted(PRIMARY_FILES):
        audit = files.get(filename, {})
        lines.extend([f"### `{filename}`", ""])
        for field, values in audit.get("enumerations", {}).items():
            lines.append(f"**{field}**")
            lines.append("")
            lines.append(markdown_table(["值", "频次"], [[key, value] for key, value in values.items()]))
            lines.append("")

    lines.extend(["## 数值异常", ""])
    anomaly_rows = []
    for filename, audit in files.items():
        anomaly = audit.get("anomalies", {})
        numeric = audit.get("numeric", {})
        anomaly_rows.append([filename, anomaly.get("nonpositive_prices", {}), anomaly.get("negative_quantities", {}), anomaly.get("last_qty_greater_than_order_qty", 0), anomaly.get("cum_qty_greater_than_order_qty", 0), anomaly.get("negative_leaves_qty", 0), anomaly.get("quantity_without_execution_price", 0), len(anomaly.get("wallet_balance_jump_candidates", []))])
    lines.append(markdown_table(["文件", "非正价格", "负数量", "lastQty>orderQty", "cumQty>orderQty", "leavesQty<0", "有量无成交价", "余额跳变候选"], anomaly_rows))
    lines.extend(["", "### 极端数值（仅报告，不自动判断为错误）", ""])
    extreme_rows = []
    for filename, audit in files.items():
        for field, stats in audit.get("numeric", {}).items():
            extreme_rows.append([filename, field, stats.get("count"), stats.get("min"), stats.get("max"), stats.get("p99_absolute"), stats.get("top_absolute_values", [])[:3]])
    lines.append(markdown_table(["文件", "字段", "有效数", "最小", "最大", "绝对值 P99", "绝对值最大示例"], extreme_rows))
    wallet = files.get("api-v1-user-walletHistory.csv", {}).get("anomalies", {}).get("wallet_balance_jump_candidates", [])
    if wallet:
        lines.extend(["", "### walletBalance 跳变候选（按原始单位的绝对变化排序）", "", markdown_table(["币种", "时间", "类型", "前余额", "当前余额", "变化", "相对变化"], [[row.get("currency"), row.get("timestamp"), row.get("transactType"), row.get("previous_balance_raw"), row.get("current_balance_raw"), row.get("delta_raw"), row.get("relative_change")] for row in wallet])])

    unit = data["unit_context"]
    lines.extend(["", "## BitMEX 单位风险", "", unit["raw_unit_risk"]["interpretation"], "", "### wallet-assets scale 观测", ""])
    scale_rows = [[currency, details.get("majorCurrency"), details.get("scale"), details.get("currencyType"), details.get("isMarginCurrency")] for currency, details in sorted(unit["wallet_asset_scales"].items())]
    lines.append(markdown_table(["currency", "majorCurrency", "scale", "类型", "保证金币种"], scale_rows))
    lines.extend(["", "需要后续标准化的字段：", "", "- 钱包历史与 wallet/margin snapshot 的 `amount`、`fee`、`walletBalance`、`marginBalance`：按 `currency` 查 `wallet-assets.scale`。", "- 成交表的 `execCost`、`execComm`、`realisedPnl`、`homeNotional`、`foreignNotional`：结合 `currency`、`settlCurrency`、`symbol` 对照 instrument 元数据。", "- 订单/成交的 `orderQty`、`lastQty`、`cumQty`、`leavesQty`、`displayQty`：合约数量，不应直接当 BTC 金额。", "- `price`、`lastPx`、`avgPx`、`stopPx`：报价价格；需按 instrument 的 quote/settle 语义解释。", "- `derived-equity-curve.csv`：已是派生的 XBT 等值曲线，必须按其 methodology 使用，不能当作原始钱包账本。", ""])

    lines.extend(["## 阻塞后续仓位重建的问题", ""])
    if readiness["blockers"]:
        lines.extend(["阻塞项：", ""] + [f"- {item}" for item in readiness["blockers"]])
    else:
        lines.append("当前没有达到审计规则阈值的硬阻塞项。")
    if readiness["caveats"]:
        lines.extend(["", "注意事项：", ""] + [f"- {item}" for item in readiness["caveats"]])

    lines.extend(["", "## M0-02 建议", ""] + [f"- {item}" for item in data["m0_02_suggestions"]])
    lines.extend(["", "## 机器可读输出", "", "完整结构化结果见同目录的 `data_audit.json`。", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the repository's BitMEX CSV/manifest data without modifying source files.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root; defaults to the repository containing this script.")
    parser.add_argument("--report-dir", type=Path, default=None, help="Report directory; defaults to <root>/quant/reports.")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="CSV batch size for Polars; stdlib fallback remains row streaming.")
    args = parser.parse_args(argv)
    report_dir = args.report_dir or args.root / "quant" / "reports"
    data = audit_dataset(args.root.resolve(), report_dir.resolve(), batch_size=max(1, args.batch_size))
    print(f"M0-01 audit completed: {data['readiness']['status']}")
    print(f"Markdown report: {report_dir / 'data_audit.md'}")
    print(f"JSON report: {report_dir / 'data_audit.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
