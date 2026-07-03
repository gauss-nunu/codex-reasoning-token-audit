#!/usr/bin/env python3
"""
Privacy-preserving Codex reasoning_output_tokens audit.

This script scans local Codex session JSONL files and prints aggregate counts only.
It does not print prompts, assistant messages, session IDs, local paths, or filenames
unless --show-files is passed.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def pct(part: int, total: int) -> float:
    return round((part / total * 100.0), 2) if total else 0.0


def safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def safe_scalar(value, default="unknown") -> str:
    if value is None:
        return default
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def parse_timestamp(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def bucket_for(dt, grain: str) -> str:
    if not dt:
        return "unknown"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    if grain == "month":
        return f"{dt.year:04d}-{dt.month:02d}"
    if grain == "week":
        iso = dt.isocalendar()
        return f"{iso.year:04d}-W{iso.week:02d}"
    if grain == "day":
        return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
    return "all"


def percentile(values, p: float):
    if not values:
        return 0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def range_bucket(value: int, ranges: list[tuple[int, int, str]]) -> str:
    for low, high, label in ranges:
        if low <= value <= high:
            return label
    return "unknown"


OUTPUT_BUCKETS = [
    (0, 250, "output_0_250"),
    (251, 500, "output_251_500"),
    (501, 1000, "output_501_1000"),
    (1001, 2000, "output_1001_2000"),
    (2001, 999999999, "output_2001_plus"),
]

INPUT_BUCKETS = [
    (0, 20000, "input_0_20k"),
    (20001, 50000, "input_20k_50k"),
    (50001, 100000, "input_50k_100k"),
    (100001, 200000, "input_100k_200k"),
    (200001, 999999999, "input_200k_plus"),
]

BUCKET_ORDER = {
    "all": 0,
    **{label: index for index, (_, _, label) in enumerate(OUTPUT_BUCKETS, start=1)},
    **{label: index for index, (_, _, label) in enumerate(INPUT_BUCKETS, start=1)},
}


def size_bucket_for(row, bucket_by: str) -> str:
    if bucket_by == "output":
        return range_bucket(row["output"], OUTPUT_BUCKETS)
    if bucket_by == "input":
        return range_bucket(row["input"], INPUT_BUCKETS)
    return "all"


def median_ratio(items) -> float:
    ratios = [(row["reasoning"] / row["output"]) for row in items if row["output"]]
    return statistics.median(ratios) if ratios else 0


def metrics_for(items):
    values = [row["reasoning"] for row in items]
    outputs = [row["output"] for row in items]
    inputs = [row["input"] for row in items]
    zeros = sum(1 for value in values if value == 0)
    exact_516 = sum(1 for value in values if value == 516)
    exact_1034 = sum(1 for value in values if value == 1034)
    exact_1552 = sum(1 for value in values if value == 1552)
    ge_516 = sum(1 for value in values if value >= 516)

    return {
        "token_count_records": len(values),
        "reasoning_zero": zeros,
        "reasoning_zero_pct": pct(zeros, len(values)),
        "reasoning_nonzero": len(values) - zeros,
        "reasoning_le_128_pct": pct(sum(1 for value in values if value <= 128), len(values)),
        "reasoning_le_256_pct": pct(sum(1 for value in values if value <= 256), len(values)),
        "reasoning_le_516_pct": pct(sum(1 for value in values if value <= 516), len(values)),
        "reasoning_median": statistics.median(values) if values else 0,
        "reasoning_mean": round(statistics.mean(values), 2) if values else 0,
        "reasoning_p75": round(percentile(values, 0.75), 2) if values else 0,
        "reasoning_p90": round(percentile(values, 0.9), 2) if values else 0,
        "reasoning_p95": round(percentile(values, 0.95), 2) if values else 0,
        "reasoning_p99": round(percentile(values, 0.99), 2) if values else 0,
        "reasoning_max": max(values) if values else 0,
        "exact_516": exact_516,
        "exact_516_pct": pct(exact_516, len(values)),
        "exact_1034": exact_1034,
        "exact_1034_pct": pct(exact_1034, len(values)),
        "exact_1552": exact_1552,
        "exact_1552_pct": pct(exact_1552, len(values)),
        "exact_516_over_ge_516_pct": pct(exact_516, ge_516),
        "input_median": statistics.median(inputs) if inputs else 0,
        "output_median": statistics.median(outputs) if outputs else 0,
        "reasoning_per_output_median": round(median_ratio(items), 4),
    }


def row_matches(row, args) -> bool:
    checks = [
        ("source", args.source),
        ("model", args.model),
        ("effort", args.effort),
        ("phase", args.phase),
    ]
    return all(value is None or row.get(field) == value for field, value in checks)


def scan_file(path: Path):
    session_source = None
    originator = None
    cli_version = None
    current_model = None
    current_effort = None
    compacted = False

    rows = []

    try:
        fh = path.open("r", encoding="utf-8")
    except Exception:
        return rows

    with fh:
        for line_no, line in enumerate(fh, 1):
            try:
                obj = json.loads(line)
            except Exception:
                continue

            typ = obj.get("type")
            payload = obj.get("payload") or {}

            if typ == "session_meta":
                meta = payload
                session_source = meta.get("source")
                originator = meta.get("originator")
                cli_version = meta.get("cli_version")
                continue

            if typ == "compacted":
                compacted = True
                continue

            if typ == "turn_context":
                current_model = payload.get("model") or current_model
                current_effort = (
                    payload.get("model_reasoning_effort")
                    or payload.get("reasoning_effort")
                    or payload.get("effort")
                    or current_effort
                )
                continue

            if typ != "event_msg":
                continue

            if payload.get("type") != "token_count":
                continue

            usage = ((payload.get("info") or {}).get("last_token_usage") or {})
            reasoning = safe_int(usage.get("reasoning_output_tokens"))
            output = safe_int(usage.get("output_tokens"))
            input_tokens = safe_int(usage.get("input_tokens"))
            if reasoning is None:
                continue

            rows.append(
                {
                    "timestamp": obj.get("timestamp"),
                    "bucket_dt": parse_timestamp(obj.get("timestamp")),
                    "source": safe_scalar(session_source),
                    "originator": safe_scalar(originator),
                    "cli_version": safe_scalar(cli_version),
                    "model": safe_scalar(current_model),
                    "effort": safe_scalar(current_effort),
                    "phase": "post_compaction" if compacted else "pre_compaction",
                    "reasoning": reasoning,
                    "output": output or 0,
                    "input": input_tokens or 0,
                    "line_no": line_no,
                    "file": str(path),
                }
            )

    return rows


def build_summary_rows(rows, args):
    groups = defaultdict(list)
    for row in rows:
        if not row_matches(row, args):
            continue
        key = (
            bucket_for(row.get("bucket_dt"), args.time_grain),
            size_bucket_for(row, args.bucket_by),
            row["source"],
            row["originator"],
            row["model"],
            row["effort"],
            row["phase"],
        )
        groups[key].append(row)

    summary_rows = []
    for key, items in groups.items():
        if len(items) < args.min_records:
            continue

        time_bucket, size_bucket, source, originator, model, effort, phase = key
        summary_rows.append(
            {
                "time_bucket": time_bucket,
                "size_bucket": size_bucket,
                "source": source,
                "originator": originator,
                "model": model,
                "effort": effort,
                "phase": phase,
                **metrics_for(items),
            }
        )

    if args.sort_by == "records":
        summary_rows.sort(key=lambda row: (-row["token_count_records"], row["time_bucket"], row["size_bucket"]))
    elif args.sort_by == "zero-rate":
        summary_rows.sort(key=lambda row: (-row["reasoning_zero_pct"], -row["token_count_records"], row["time_bucket"]))
    elif args.sort_by == "exact516-rate":
        summary_rows.sort(key=lambda row: (-row["exact_516_pct"], -row["token_count_records"], row["time_bucket"]))
    elif args.sort_by == "exact516-over-ge516":
        summary_rows.sort(key=lambda row: (-row["exact_516_over_ge_516_pct"], -row["token_count_records"], row["time_bucket"]))
    else:
        summary_rows.sort(
            key=lambda row: (
                row["time_bucket"],
                BUCKET_ORDER.get(row["size_bucket"], 999),
                row["source"],
                row["model"],
                row["phase"],
                -row["token_count_records"],
            )
        )

    if args.top:
        summary_rows = summary_rows[: args.top]

    return summary_rows


def print_text_summary(rows, summary_rows, args):
    print("Codex reasoning_output_tokens audit")
    print(f"records: {len(rows)}")
    print(f"time_grain: {args.time_grain}")
    print(f"bucket_by: {args.bucket_by}")
    print()

    for row in summary_rows:
        print(
            f"time_bucket={row['time_bucket']} size_bucket={row['size_bucket']} "
            f"source={row['source']} originator={row['originator']} model={row['model']} "
            f"effort={row['effort']} phase={row['phase']}"
        )
        print(f"  token_count_records: {row['token_count_records']}")
        print(f"  reasoning_zero: {row['reasoning_zero']} ({row['reasoning_zero_pct']}%)")
        print(f"  reasoning_nonzero: {row['reasoning_nonzero']}")
        print(f"  reasoning_le_128_pct: {row['reasoning_le_128_pct']}%")
        print(f"  reasoning_le_256_pct: {row['reasoning_le_256_pct']}%")
        print(f"  reasoning_le_516_pct: {row['reasoning_le_516_pct']}%")
        print(f"  reasoning_median: {row['reasoning_median']}")
        print(f"  reasoning_mean: {row['reasoning_mean']}")
        print(f"  reasoning_p75: {row['reasoning_p75']}")
        print(f"  reasoning_p90: {row['reasoning_p90']}")
        print(f"  reasoning_p95: {row['reasoning_p95']}")
        print(f"  reasoning_p99: {row['reasoning_p99']}")
        print(f"  reasoning_max: {row['reasoning_max']}")
        print(f"  exact_516: {row['exact_516']} ({row['exact_516_pct']}%)")
        print(f"  exact_1034: {row['exact_1034']} ({row['exact_1034_pct']}%)")
        print(f"  exact_1552: {row['exact_1552']} ({row['exact_1552_pct']}%)")
        print(f"  exact_516_over_ge_516: {row['exact_516_over_ge_516_pct']}%")
        print(f"  input_median: {row['input_median']}")
        print(f"  output_median: {row['output_median']}")
        print(f"  reasoning_per_output_median: {row['reasoning_per_output_median']}")
        print()


def print_csv_summary(summary_rows):
    if not summary_rows:
        return
    fieldnames = list(summary_rows[0].keys())
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(summary_rows)


def summarize(rows, show_files: bool, args):
    summary_rows = build_summary_rows(rows, args)

    if args.format == "csv":
        print_csv_summary(summary_rows)
    else:
        print_text_summary(rows, summary_rows, args)

    if show_files:
        print("Files scanned:")
        for file_name in sorted({r["file"] for r in rows}):
            print(f"  {file_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--codex-home",
        default=str(Path.home() / ".codex"),
        help="Codex home directory. Default: ~/.codex",
    )
    parser.add_argument(
        "--show-files",
        action="store_true",
        help="Print scanned filenames. Off by default for privacy.",
    )
    parser.add_argument(
        "--time-grain",
        choices=["all", "month", "week", "day"],
        default="all",
        help="Group output by all records, month, ISO week, or day.",
    )
    parser.add_argument(
        "--bucket-by",
        choices=["none", "output", "input"],
        default="none",
        help="Also group by output-token or input-token bucket.",
    )
    parser.add_argument("--source", help="Filter by session source, for example vscode or exec.")
    parser.add_argument("--model", help="Filter by displayed model, for example gpt-5.5.")
    parser.add_argument("--effort", help="Filter by displayed reasoning effort, for example xhigh.")
    parser.add_argument(
        "--phase",
        choices=["pre_compaction", "post_compaction"],
        help="Filter by compaction phase.",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=1,
        help="Only print groups with at least this many token_count records.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["default", "records", "zero-rate", "exact516-rate", "exact516-over-ge516"],
        default="default",
        help="Sort output groups.",
    )
    parser.add_argument("--top", type=int, help="Print only the first N groups after sorting.")
    parser.add_argument(
        "--format",
        choices=["text", "csv"],
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    root = Path(args.codex_home)
    session_root = root / "sessions"
    rows = []

    for path in session_root.rglob("*.jsonl"):
        rows.extend(scan_file(path))

    summarize(rows, args.show_files, args)


if __name__ == "__main__":
    main()
