# Sample Output

Example aggregate output from one local environment. Values can drift as new Codex sessions are added locally:

```text
Codex reasoning_output_tokens audit
records: 45586
time_grain: all
bucket_by: none

time_bucket=all size_bucket=all source=vscode originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=post_compaction
  token_count_records: 36153
  reasoning_zero: 7727 (21.37%)
  reasoning_nonzero: 28426
  reasoning_le_128_pct: 69.21%
  reasoning_le_256_pct: 78.6%
  reasoning_le_516_pct: 92.82%
  reasoning_median: 43
  reasoning_mean: 184.36
  reasoning_p75: 199.0
  reasoning_p90: 516.0
  reasoning_p95: 762.0
  reasoning_p99: 1854.0
  reasoning_max: 10326
  exact_516: 1999 (5.53%)
  exact_1034: 271 (0.75%)
  exact_1552: 61 (0.17%)
  exact_516_over_ge_516: 43.55%
  input_median: 144982
  output_median: 350
  reasoning_per_output_median: 0.1293

time_bucket=all size_bucket=all source=vscode originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=pre_compaction
  token_count_records: 6562
  reasoning_zero: 1297 (19.77%)
  reasoning_nonzero: 5265
  reasoning_le_128_pct: 49.18%
  reasoning_le_256_pct: 58.61%
  reasoning_le_516_pct: 85.09%
  reasoning_median: 148.0
  reasoning_mean: 391.82
  reasoning_p75: 516.0
  reasoning_p90: 1007.0
  reasoning_p95: 1552.0
  reasoning_p99: 3464.78
  reasoning_max: 11974
  exact_516: 1128 (17.19%)
  exact_1034: 98 (1.49%)
  exact_1552: 44 (0.67%)
  exact_516_over_ge_516: 53.31%
  input_median: 99096.0
  output_median: 559.0
  reasoning_per_output_median: 0.3168

time_bucket=all size_bucket=all source=vscode originator=Codex Desktop model=gpt-5.4 effort=xhigh phase=pre_compaction
  token_count_records: 1762
  reasoning_zero: 120 (6.81%)
  reasoning_nonzero: 1642
  reasoning_le_128_pct: 50.62%
  reasoning_le_256_pct: 62.66%
  reasoning_le_516_pct: 79.97%
  reasoning_median: 122.5
  reasoning_mean: 682.76
  reasoning_p75: 516.0
  reasoning_p90: 1664.9
  reasoning_p95: 2512.0
  reasoning_p99: 5511.44
  reasoning_max: 17653
  exact_516: 76 (4.31%)
  exact_1034: 8 (0.45%)
  exact_1552: 8 (0.45%)
  exact_516_over_ge_516: 16.49%
  input_median: 29617.5
  output_median: 473.0
  reasoning_per_output_median: 0.3161

time_bucket=all size_bucket=all source=exec originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=pre_compaction
  token_count_records: 46
  reasoning_zero: 0 (0.0%)
  reasoning_nonzero: 46
  reasoning_le_128_pct: 0.0%
  reasoning_le_256_pct: 0.0%
  reasoning_le_516_pct: 60.87%
  reasoning_median: 516.0
  reasoning_mean: 833.04
  reasoning_p75: 1034.0
  reasoning_p90: 1970.0
  reasoning_p95: 2070.0
  reasoning_p99: 2521.4
  reasoning_max: 2890
  exact_516: 12 (26.09%)
  exact_1034: 6 (13.04%)
  exact_1552: 2 (4.35%)
  exact_516_over_ge_516: 40.0%
  input_median: 32717.0
  output_median: 805.0
  reasoning_per_output_median: 0.6821
```

This sample omits prompts, assistant messages, session IDs, local paths, and filenames.

Time-series examples:

```bash
python codex_reasoning_zero_audit.py --time-grain month
python codex_reasoning_zero_audit.py --time-grain week
```
