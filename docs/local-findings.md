# Local Findings Snapshot

Snapshot date: 2026-07-04

These results come from one local Codex telemetry dataset. Values can drift as new local sessions are added.

## Weekly Zero-Reasoning Signal: `gpt-5.5 / xhigh / vscode / pre_compaction`

This is the simplest first-read signal: completed turns where telemetry reported `reasoning_output_tokens=0`.

| Week | Records | Zero % |
| --- | ---: | ---: |
| 2026-W18 | 868 | 22.81 |
| 2026-W19 | 332 | 25.00 |
| 2026-W20 | 276 | 22.46 |
| 2026-W21 | 109 | 57.80 |
| 2026-W22 | 292 | 17.12 |
| 2026-W23 | 524 | 22.90 |
| 2026-W24 | 1,190 | 14.62 |
| 2026-W25 | 898 | 15.81 |
| 2026-W26 | 1,090 | 15.69 |
| 2026-W27 | 1,181 | 23.20 |

Across these weekly buckets, the weighted zero-rate was 19.78% over 6,760 completed-turn records.

## Monthly Core: `gpt-5.5 / xhigh / vscode / pre_compaction`

| Month | Records | Zero % | `<=516` % | Median | Mean | P90 | Exact 516 % | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-04 | 682 | 18.48 | 90.18 | 74.0 | 255.69 | 516.0 | 7.33 | 42.74 |
| 2026-05 | 1,195 | 27.62 | 90.96 | 54 | 263.85 | 516.0 | 11.13 | 55.19 |
| 2026-06 | 4,282 | 16.84 | 82.74 | 213.0 | 440.62 | 1034.0 | 19.57 | 53.14 |
| 2026-07 | 601 | 26.62 | 81.70 | 331 | 464.11 | 1140.0 | 25.62 | 58.33 |

The main pattern is a high zero-rate plus a rising exact-516 share. Among turns that reached at least 516 reasoning tokens, around half or more landed exactly on 516.

## Output-Length Buckets: `gpt-5.5 / xhigh / vscode / pre_compaction`

| Output tokens | Records | Zero % | `<=516` % | Median reasoning | P90 reasoning | Exact 516 % | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-250 | 1,533 | 38.29 | 100.00 | 12 | 71.0 | 0.00 | 0.00 |
| 251-500 | 1,585 | 27.13 | 100.00 | 52 | 232.2 | 0.00 | 0.00 |
| 501-1000 | 1,896 | 13.66 | 95.20 | 372.0 | 516.0 | 31.59 | 86.81 |
| 1001-2000 | 1,167 | 3.08 | 59.90 | 516 | 1113.8 | 46.02 | 53.43 |
| 2001+ | 579 | 4.32 | 19.69 | 1587 | 3716.4 | 6.74 | 7.74 |

The `501-1000` output-token band is especially notable: if a turn reached at least 516 reasoning tokens, it landed exactly on 516 in 86.81% of cases.

## Input-Context Buckets: `gpt-5.5 / xhigh / vscode / pre_compaction`

| Input tokens | Records | Zero % | `<=516` % | Median reasoning | P90 reasoning | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-20k | 228 | 8.33 | 93.86 | 372.5 | 516.0 | 84.95 |
| 20k-50k | 1,306 | 15.01 | 83.69 | 330.0 | 1008.5 | 61.13 |
| 50k-100k | 1,860 | 15.75 | 80.22 | 165.0 | 1133.4 | 42.41 |
| 100k-200k | 2,889 | 25.72 | 87.23 | 85 | 880.2 | 54.16 |
| 200k+ | 477 | 18.03 | 87.42 | 66 | 837.6 | 47.37 |

Longer input context does not automatically correspond to higher reasoning-token usage in this local dataset.

## Highest Zero-Rate Day Spikes

Filtered to `gpt-5.5 / xhigh / vscode / pre_compaction` with at least 30 records per day.

| Day | Records | Zero % | Median reasoning | P90 reasoning | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-05-19 | 62 | 61.29 | 0.0 | 516.0 | 80.00 |
| 2026-05-18 | 31 | 61.29 | 0 | 1006.0 | 50.00 |
| 2026-07-01 | 80 | 41.25 | 249.5 | 904.1 | 66.67 |
| 2026-05-03 | 186 | 38.71 | 24.0 | 516.0 | 71.43 |
| 2026-06-04 | 51 | 37.25 | 167 | 963.0 | 52.94 |
| 2026-05-07 | 170 | 37.06 | 25.0 | 516.0 | 58.33 |
| 2026-06-19 | 210 | 30.48 | 273.5 | 1034.0 | 54.12 |
| 2026-04-30 | 244 | 30.33 | 41.0 | 508.5 | 64.00 |
| 2026-06-05 | 59 | 28.81 | 68 | 516.0 | 81.82 |
| 2026-07-03 | 245 | 28.16 | 326 | 1401.2 | 59.09 |

These day-level spikes make the behavior look bursty rather than evenly distributed.
