# Local Findings Snapshot

Snapshot date: 2026-07-03

These results come from one local Codex telemetry dataset. Values can drift as new local sessions are added.

## Monthly Core: `gpt-5.5 / xhigh / vscode / pre_compaction`

| Month | Records | Zero % | `<=516` % | Median | Mean | P90 | Exact 516 % | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-04 | 682 | 18.48 | 90.18 | 74.0 | 255.69 | 516.0 | 7.33 | 42.74 |
| 2026-05 | 1,195 | 27.62 | 90.96 | 54 | 263.85 | 516.0 | 11.13 | 55.19 |
| 2026-06 | 4,282 | 16.84 | 82.74 | 213.0 | 440.62 | 1034.0 | 19.57 | 53.14 |
| 2026-07 | 403 | 29.78 | 81.64 | 368 | 483.19 | 1279.2 | 26.55 | 59.12 |

The main pattern is a high zero-rate plus a rising exact-516 share. Among turns that reached at least 516 reasoning tokens, around half or more landed exactly on 516.

## Output-Length Buckets: `gpt-5.5 / xhigh / vscode / pre_compaction`

| Output tokens | Records | Zero % | `<=516` % | Median reasoning | P90 reasoning | Exact 516 % | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-250 | 1,491 | 38.30 | 100.00 | 12 | 71.0 | 0.00 | 0.00 |
| 251-500 | 1,543 | 26.90 | 100.00 | 52 | 232.6 | 0.00 | 0.00 |
| 501-1000 | 1,831 | 13.65 | 95.14 | 366 | 516.0 | 30.91 | 86.41 |
| 1001-2000 | 1,131 | 3.18 | 60.57 | 516 | 1110.0 | 46.33 | 54.02 |
| 2001+ | 566 | 4.42 | 19.96 | 1552.0 | 3733.5 | 6.71 | 7.74 |

The `501-1000` output-token band is especially notable: if a turn reached at least 516 reasoning tokens, it landed exactly on 516 in 86.41% of cases.

## Input-Context Buckets: `gpt-5.5 / xhigh / vscode / pre_compaction`

| Input tokens | Records | Zero % | `<=516` % | Median reasoning | P90 reasoning | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-20k | 225 | 8.44 | 93.78 | 370 | 516.0 | 84.44 |
| 20k-50k | 1,279 | 15.17 | 83.58 | 309 | 1008.2 | 60.15 |
| 50k-100k | 1,827 | 15.82 | 80.35 | 165 | 1115.6 | 42.74 |
| 100k-200k | 2,761 | 25.68 | 87.40 | 85 | 846.0 | 54.45 |
| 200k+ | 470 | 18.30 | 87.87 | 63.0 | 770.7 | 47.22 |

Longer input context does not automatically correspond to higher reasoning-token usage in this local dataset.

## Highest Zero-Rate Day Spikes

Filtered to `gpt-5.5 / xhigh / vscode / pre_compaction` with at least 30 records per day.

| Day | Records | Zero % | Median reasoning | P90 reasoning | Exact 516 / `>=516` |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-05-19 | 62 | 61.29 | 0.0 | 516.0 | 80.00 |
| 2026-05-18 | 31 | 61.29 | 0 | 1006.0 | 50.00 |
| 2026-07-01 | 80 | 41.25 | 249.5 | 904.1 | 66.67 |
| 2026-05-03 | 186 | 38.71 | 24.0 | 516.0 | 71.43 |

These day-level spikes make the behavior look bursty rather than evenly distributed.

