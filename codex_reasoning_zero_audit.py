#!/usr/bin/env python3
"""
Privacy-preserving Codex reasoning_output_tokens audit.

This script scans local Codex session JSONL files and prints aggregate counts only.
It does not print prompts, assistant messages, session IDs, local paths, or filenames
unless --show-files is passed.
"""

from __future__ import annotations

import argparse
import json
import statistics
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


def summarize(rows, show_files: bool, time_grain: str):
    groups = defaultdict(list)
    for row in rows:
        key = (
            bucket_for(row.get("bucket_dt"), time_grain),
            row["source"],
            row["originator"],
            row["model"],
            row["effort"],
            row["phase"],
        )
        groups[key].append(row)

    print("Codex reasoning_output_tokens audit")
    print(f"records: {len(rows)}")
    print(f"time_grain: {time_grain}")
    print()

    for key, items in sorted(groups.items(), key=lambda kv: (kv[0][0], -len(kv[1]), kv[0])):
        bucket, source, originator, model, effort, phase = key
        values = [r["reasoning"] for r in items]
        outputs = [r["output"] for r in items]
        zeros = sum(1 for v in values if v == 0)
        nonzero = len(values) - zeros
        exact_516 = sum(1 for v in values if v == 516)
        exact_1034 = sum(1 for v in values if v == 1034)
        exact_1552 = sum(1 for v in values if v == 1552)
        ge_516 = sum(1 for v in values if v >= 516)

        print(
            f"bucket={bucket} source={source} originator={originator} model={model} "
            f"effort={effort} phase={phase}"
        )
        print(f"  token_count_records: {len(values)}")
        print(f"  reasoning_zero: {zeros} ({pct(zeros, len(values))}%)")
        print(f"  reasoning_nonzero: {nonzero}")
        print(f"  reasoning_median: {statistics.median(values) if values else 0}")
        print(f"  reasoning_mean: {round(statistics.mean(values), 2) if values else 0}")
        print(f"  reasoning_p90: {round(percentile(values, 0.9), 2) if values else 0}")
        print(f"  reasoning_max: {max(values) if values else 0}")
        print(f"  exact_516: {exact_516} ({pct(exact_516, len(values))}%)")
        print(f"  exact_1034: {exact_1034} ({pct(exact_1034, len(values))}%)")
        print(f"  exact_1552: {exact_1552} ({pct(exact_1552, len(values))}%)")
        print(f"  exact_516_over_ge_516: {pct(exact_516, ge_516)}%")
        print(f"  output_median: {statistics.median(outputs) if outputs else 0}")
        print()

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
    args = parser.parse_args()

    root = Path(args.codex_home)
    session_root = root / "sessions"
    rows = []

    for path in session_root.rglob("*.jsonl"):
        rows.extend(scan_file(path))

    summarize(rows, args.show_files, args.time_grain)


if __name__ == "__main__":
    main()
