# Codex Desktop gpt-5.5 xhigh: high rate of telemetry-reported reasoning_output_tokens=0 in GUI path

## Summary

I observed a large path-dependent gap between Codex Desktop GUI sessions and CLI replay sessions for telemetry-reported `reasoning_output_tokens`.

In the Desktop GUI session, many completed turns had telemetry-reported `reasoning_output_tokens=0` despite the displayed model/effort setting being `gpt-5.5 / xhigh`. In comparable CLI replay sessions, the same high zero-rate did not appear.

This may be related to existing reports about Codex Desktop / `gpt-5.5` / `xhigh` behavior, including direct-final runs with exactly 516 reasoning tokens and broader clustering around 516 / 1034 / 1552.

## Environment

- Product: Codex Desktop app
- Platform: Windows
- Codex version shown in session metadata: `0.142.5`
- Model setting shown in turn context: `gpt-5.5`
- Reasoning effort shown in turn context: `xhigh`
- GUI session source: `vscode`
- CLI replay source: `exec`
- Observation date: 2026-07-03

For both GUI and CLI samples, I verified that session metadata or turn context showed the displayed model as `gpt-5.5`, displayed reasoning effort as `xhigh`, and source as `vscode` for GUI vs `exec` for CLI.

I understand the GUI and CLI paths are not identical execution environments. The point of the comparison is that the anomaly appears path-dependent: it is prominent in the Desktop GUI / `vscode` path and absent or much weaker in CLI / `exec` replays using the same displayed model and effort.

## Main observations

### Broader local aggregate

Across local Codex session JSONL files, without printing prompts, assistant messages, session IDs, local paths, or filenames:

- Total `token_count` records scanned: 45,499
- Desktop GUI `gpt-5.5 / xhigh`, pre-compaction:
  - Records: 6,562
  - `reasoning_output_tokens=0`: 1,297
  - Zero rate: 19.77%
- Desktop GUI `gpt-5.5 / xhigh`, post-compaction:
  - Records: 36,066
  - `reasoning_output_tokens=0`: 7,680
  - Zero rate: 21.29%
- Desktop GUI `gpt-5.4 / xhigh`, pre-compaction:
  - Records: 1,762
  - `reasoning_output_tokens=0`: 120
  - Zero rate: 6.81%
- CLI `exec` `gpt-5.5 / xhigh`, pre-compaction:
  - Records: 46
  - `reasoning_output_tokens=0`: 0
  - Zero rate: 0%

This broader aggregate makes the specific GUI thread below look like an extreme instance of a wider Desktop `gpt-5.5 / xhigh` telemetry pattern, rather than a one-off parsing artifact.

### GUI session before first compaction

I focused on the segment before first compaction to reduce confounding from context summarization or replay effects.

- `token_count` records: 139
- `reasoning_output_tokens=0`: 60
- Zero rate: 43.2%

Completed-turn grouping:

- Completed turns: 115
- `reasoning_output_tokens=0`: 56
- Zero rate: 48.7%

### CLI replay comparison

CLI 4-turn replay:

- `token_count` records: 4
- `reasoning_output_tokens=0`: 0
- Values: 516, 1034, 2070, 1552

CLI 30-turn replay:

- Main `token_count` aggregation records: 36
- `reasoning_output_tokens=0`: 0
- Median reasoning tokens: 516
- Mean reasoning tokens: 885.9
- Max reasoning tokens: 2890
- Auxiliary completed-turn extraction found 1 zero-reasoning turn, still far below the GUI zero rate.

## Why this is not explained by short acknowledgement turns

The telemetry-reported zero-reasoning GUI turns were not mainly simple "OK" or acknowledgement responses.

For the 56 telemetry-reported zero-reasoning completed GUI turns before compaction:

- Simple acknowledgement-like turns: 0
- Short responses: 3
- Judgment / strategy / expectation-setting turns: 22
- Live situation handling turns: 8
- Investigation / meta-analysis turns: 2
- Other structural discussion turns: 21

Additional pattern:

| GUI completed turns before compaction | Count |
| --- | ---: |
| telemetry-reported `reasoning_output_tokens=0` | 56 |
| zero-reasoning turns with a visible `reasoning` response item | 1 / 56 |
| zero-reasoning turns with tool calls | 0 / 56 |

So the common pattern was a direct-final-like path without visible intermediate reasoning items or tool use.

## Timing / output-size comparison

GUI telemetry-reported zero-reasoning group:

- Median input tokens: 74,578
- Median output tokens: 388.5
- Median assistant text length: 550 characters
- Median duration: 10.7 seconds
- Median time-to-first-token: 2.6 seconds

GUI nonzero-reasoning group:

- Median input tokens: 83,247
- Median output tokens: 956
- Median assistant text length: 590 characters
- Median duration: 22.4 seconds
- Median time-to-first-token: 12.7 seconds

The assistant text length medians are close, while timing differs sharply. Output length alone does not explain the high zero-reasoning rate.

This report is primarily about the telemetry/path discrepancy, not a claim that every zero-reasoning turn was wrong. The concern is that a high zero-rate under `xhigh` may indicate a GUI-specific routing, effort propagation, telemetry, or response-stream handling issue.

## Related public issues

- `openai/codex#29353`: Codex Desktop / `gpt-5.5` / `xhigh` short-circuit behavior where direct final answers with exactly 516 reasoning tokens returned wrong answers, while longer reasoning runs returned correct answers.
- `openai/codex#30364`: aggregate `token_count` evidence showing clustering around 516 / 1034 / 1552 reasoning tokens.

## Privacy note

I am not attaching raw session JSONL because it contains private conversation content, local paths, session IDs, and other user-specific data. The numbers above are aggregated from local session telemetry.

I do not have server-side routing visibility or final `response.model` for the GUI turn. This report is based on local Codex session telemetry.

## Ask

Please investigate whether Codex Desktop GUI sessions can produce a direct-final path with telemetry-reported zero or unusually low `reasoning_output_tokens` despite `gpt-5.5 / xhigh` being selected.

In particular, please compare the Desktop GUI / `vscode` path with CLI / `exec` sessions using the same displayed model and reasoning-effort setting, and check whether this reflects:

- GUI-specific routing or fallback behavior
- reasoning-effort propagation failure
- response-stream / phase handling differences
- `token_count` telemetry under-reporting
- a valid but undocumented direct-final path for `xhigh`

I am not claiming that `reasoning_output_tokens=0` proves no internal reasoning occurred. The issue is the large path-dependent discrepancy: GUI completed turns show a high zero-rate, while comparable CLI replays do not.
