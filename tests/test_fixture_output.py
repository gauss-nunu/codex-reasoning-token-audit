#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "codex_reasoning_zero_audit.py"
FIXTURE_HOME = ROOT / "tests" / "fixtures" / "minimal_codex_home"


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--codex-home", str(FIXTURE_HOME)],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        return result.returncode

    output = result.stdout
    expected = [
        "records: 3",
        "source=vscode originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=pre_compaction",
        "token_count_records: 2",
        "reasoning_zero: 1 (50.0%)",
        "source=vscode originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=post_compaction",
        "token_count_records: 1",
        "reasoning_zero: 1 (100.0%)",
    ]

    missing = [line for line in expected if line not in output]
    if missing:
        print("Missing expected output:")
        for line in missing:
            print(f"  {line}")
        print("\nActual output:")
        print(output)
        return 1

    print("fixture test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

