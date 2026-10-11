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


def instance(label):
    """THIS REQUIRES assignment_data.py (same adapter as run_all.py)."""
    from run_all import load_instances
    return load_instances()[label]
