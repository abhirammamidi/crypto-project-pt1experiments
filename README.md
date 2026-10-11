# Experiments

The supplied experiment scripts are retained for reproducibility. Run them from this directory with the parent directory on `PYTHONPATH`, for example:

```bash
PYTHONPATH=.. python exp_ic_B.py --instances F --bounds 180,260,400 --max-trials 500000
PYTHONPATH=.. python exp_ls_vs_ic.py
```

The G linear-sieve comparison is expected to report an underdetermined system for the original B/M settings. Do not describe it as a successful solve. The script is a comparison harness; it does not overcome the dense-matrix scalability issue.
