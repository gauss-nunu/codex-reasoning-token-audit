# Sample Output

Example aggregate output from one local environment. Values can drift as new Codex sessions are added locally:

```text
Codex reasoning_output_tokens audit
records: 45499

source=vscode originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=post_compaction
  token_count_records: 36066
  reasoning_zero: 7680 (21.29%)
  reasoning_nonzero: 28386
  reasoning_median: 43.0
  reasoning_mean: 184.42
  reasoning_max: 10326
  output_median: 350.0

source=vscode originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=pre_compaction
  token_count_records: 6562
  reasoning_zero: 1297 (19.77%)
  reasoning_nonzero: 5265
  reasoning_median: 148.0
  reasoning_mean: 391.82
  reasoning_max: 11974
  output_median: 559.0

source=vscode originator=Codex Desktop model=gpt-5.4 effort=xhigh phase=pre_compaction
  token_count_records: 1762
  reasoning_zero: 120 (6.81%)
  reasoning_nonzero: 1642
  reasoning_median: 122.5
  reasoning_mean: 682.76
  reasoning_max: 17653
  output_median: 473.0

source=exec originator=Codex Desktop model=gpt-5.5 effort=xhigh phase=pre_compaction
  token_count_records: 46
  reasoning_zero: 0 (0.0%)
  reasoning_nonzero: 46
  reasoning_median: 516.0
  reasoning_mean: 833.04
  reasoning_max: 2890
  output_median: 805.0
```

This sample omits prompts, assistant messages, session IDs, local paths, and filenames.
