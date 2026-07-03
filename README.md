# Codex Reasoning Token Audit

Privacy-preserving telemetry audit tooling for local Codex session logs.

This project analyzes local Codex `session JSONL` telemetry and reports aggregate `reasoning_output_tokens` patterns without printing prompts, assistant messages, session IDs, local paths, or filenames by default.

## Why This Exists

Codex users have reported degraded behavior around `gpt-5.5 / xhigh`, including suspicious clustering of reasoning-token counts around fixed values such as `516`, `1034`, and `1552`.

This audit adds another angle: comparing telemetry-reported zero-reasoning-token rates across Codex Desktop GUI sessions and CLI `exec` sessions.

In one local dataset, Desktop GUI / `vscode` sessions using displayed `gpt-5.5 / xhigh` showed a much higher rate of telemetry-reported `reasoning_output_tokens=0` than CLI / `exec` replays using the same displayed model and effort.

## What It Measures

The script scans local Codex session JSONL files under `~/.codex/sessions` and aggregates:

- session source, such as `vscode` or `exec`
- originator
- displayed model
- displayed reasoning effort
- pre-compaction vs post-compaction phase
- `reasoning_output_tokens`
- `output_tokens`
- zero-rate, median, mean, and max values

It does not inspect or print private conversation content.

## Example Finding

From one local snapshot. These values can drift as new Codex sessions are added locally:

| Group | Records | `reasoning_output_tokens=0` | Zero Rate |
| --- | ---: | ---: | ---: |
| Desktop GUI `gpt-5.5 / xhigh`, pre-compaction | 6,562 | 1,297 | 19.77% |
| Desktop GUI `gpt-5.5 / xhigh`, post-compaction | 36,066 | 7,680 | 21.29% |
| Desktop GUI `gpt-5.4 / xhigh`, pre-compaction | 1,762 | 120 | 6.81% |
| CLI `exec` `gpt-5.5 / xhigh`, pre-compaction | 46 | 0 | 0.00% |

One GUI thread before first compaction was more extreme:

- `token_count` records: 139
- telemetry-reported `reasoning_output_tokens=0`: 60
- zero rate: 43.2%
- completed turns: 115
- completed turns with telemetry-reported `reasoning_output_tokens=0`: 56
- completed-turn zero rate: 48.7%

See [`docs/public-report.md`](docs/public-report.md) for the full sanitized report.

## Usage

Run:

```bash
python codex_reasoning_zero_audit.py
```

To scan a non-default Codex home directory:

```bash
python codex_reasoning_zero_audit.py --codex-home /path/to/.codex
```

By default, filenames are not printed. To show scanned files:

```bash
python codex_reasoning_zero_audit.py --show-files
```

## Tests

Run the fixture test:

```bash
python tests/test_fixture_output.py
```

Run a syntax check:

```bash
python -m py_compile codex_reasoning_zero_audit.py tests/test_fixture_output.py
```

## Privacy Model

The audit script is designed to be safe for sharing aggregate results:

- Does not print prompts
- Does not print assistant messages
- Does not print session IDs
- Does not print local paths or filenames by default
- Does not upload data
- Runs locally

Do not publish raw `.codex/sessions/*.jsonl` files. They can contain private conversation content, local paths, session IDs, and other user-specific data.

## Related Upstream Issue

This work was shared as a data point on:

- [`openai/codex#30364`](https://github.com/openai/codex/issues/30364)

The related issue discusses `gpt-5.5` reasoning-token clustering around `516 / 1034 / 1552`. This audit focuses on a related but separate path-dependent observation: telemetry-reported zero-reasoning-token rates in Desktop GUI sessions compared with CLI `exec` sessions.

## Scope

This project does not claim that `reasoning_output_tokens=0` proves no internal reasoning occurred.

The narrower claim is:

> Local Codex telemetry can show a large path-dependent discrepancy in telemetry-reported reasoning-token usage under the same displayed model and effort setting.

Potential explanations include:

- GUI-specific routing or fallback behavior
- reasoning-effort propagation differences
- response-stream or phase handling differences
- `token_count` telemetry under-reporting
- a valid but undocumented direct-final path for `xhigh`

## License

MIT
