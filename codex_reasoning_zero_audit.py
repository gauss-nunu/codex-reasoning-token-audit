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


def summarize(rows, show_files: bool):
    groups = defaultdict(list)
    for row in rows:
        key = (row["source"], row["originator"], row["model"], row["effort"], row["phase"])
        groups[key].append(row)

    print("Codex reasoning_output_tokens audit")
    print(f"records: {len(rows)}")
    print()

    for key, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        source, originator, model, effort, phase = key
        values = [r["reasoning"] for r in items]
        outputs = [r["output"] for r in items]
        zeros = sum(1 for v in values if v == 0)
        nonzero = len(values) - zeros

        print(
            f"source={source} originator={originator} model={model} "
            f"effort={effort} phase={phase}"
        )
        print(f"  token_count_records: {len(values)}")
        print(f"  reasoning_zero: {zeros} ({pct(zeros, len(values))}%)")
        print(f"  reasoning_nonzero: {nonzero}")
        print(f"  reasoning_median: {statistics.median(values) if values else 0}")
        print(f"  reasoning_mean: {round(statistics.mean(values), 2) if values else 0}")
        print(f"  reasoning_max: {max(values) if values else 0}")
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
    args = parser.parse_args()

    root = Path(args.codex_home)
    session_root = root / "sessions"
    rows = []

    for path in session_root.rglob("*.jsonl"):
        rows.extend(scan_file(path))

    summarize(rows, args.show_files)


if __name__ == "__main__":
    main()
