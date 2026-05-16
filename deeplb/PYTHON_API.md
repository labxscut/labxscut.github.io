# DeepLB Python API

## Package entrypoints

- Package name: `deeplb`
- Public import:
  - `from deeplb import run_pipeline`
- CLI entry:
  - `python -m deeplb`
  - `deeplb` (after `pip install -e .`)

## Function reference

### `run_pipeline(script_args=None, *, dry_run=False, check=True, capture_output=False)`

Thin wrapper for `Scripts/DeepLB_pipeline.sh`.

Parameters:

- `script_args` (`Sequence[str] | None`): pass-through args for shell pipeline.
- `dry_run` (`bool`): append `-d` if missing.
- `check` (`bool`): raise on non-zero shell exit.
- `capture_output` (`bool`): capture stdout/stderr.

Returns:

- `subprocess.CompletedProcess[str]`

Example:

```python
from deeplb import run_pipeline

result = run_pipeline(
    ["-r", "/path/to/DeepLB", "-t", "lihc", "-g", "TH", "-u", "part3", "-q", "0.1", "-k", "hyper", "-v", "1"],
    dry_run=True,
    check=False,
    capture_output=True,
)

print(result.returncode)
print(result.stdout)
```

## CLI wrapper reference

### `python -m deeplb`

Options:

- `--dry-run`: append `-d` to shell pipeline call.
- trailing args: forwarded to `Scripts/DeepLB_pipeline.sh`.

Examples:

```bash
python -m deeplb -h
python -m deeplb -- -r /path/to/DeepLB -t lihc -g TH -u part3 -q 0.1 -k hyper -v 1
python -m deeplb --dry-run -- -r /path/to/DeepLB -t lihc -g TH -u part3 -q 0.1 -k hyper -v 1
```

## Script-level Python components

DeepLB also contains CLI-oriented Python scripts:

- Part2 mMTS: `Scripts/Part2.Pseudo-fragment_Generation_by_mMTS/*.py`
- Part3 model: `Scripts/Part3.ResTran_model_training/training.py`
- Part3 predict: `Scripts/Part3.ResTran_model_training/predict_reads_source.py`
- Part3 risk: `Scripts/Part3.ResTran_model_training/cal_risk.py`

These are currently designed for CLI orchestration, not stable import APIs.
