"""Shared set-up for experiment scripts: import paths, results folder, CSV/plot helpers."""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PART1 = os.path.dirname(HERE)
ROOT = os.path.dirname(PART1)
for path in (PART1, ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)


def write_csv(name, header, rows):
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("wrote", path)


def get_plt():
    """matplotlib is used only for plotting (not for any core algorithm)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("matplotlib not installed - CSV written, plot skipped")
        return None


_CACHE = {}


def all_instances():
    """THIS REQUIRES assignment_data.py (found and normalised by data_loader.py, same as run_all.py)."""
    if "inst" not in _CACHE:
        import data_loader
        _CACHE["inst"], _CACHE["path"] = data_loader.load_instances(quiet=True)
        print("data file:", _CACHE["path"])
    return _CACHE["inst"]


def instance(label):
    inst = all_instances()
    if label not in inst:
        raise SystemExit(f"instance {label} is not in the data file (found: {', '.join(inst)})")
    return inst[label]
