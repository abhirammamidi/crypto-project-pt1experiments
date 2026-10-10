"""Shared setup/helpers for Part 1 experiment scripts.

Run from the project root:
    python -m experiments.exp_rho_runs
or from the experiments directory:
    python exp_rho_runs.py
"""
from __future__ import annotations
import csv
import json
import math
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def load_data():
    import assignment_data
    return assignment_data

def instance(label):
    data = load_data()
    return data.INSTANCES[label]

def verify(inst, x):
    return x is not None and pow(inst["g"], x, inst["p"]) == inst["h"]

def result_dir():
    path = PROJECT_ROOT / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path

def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(dict.fromkeys(k for row in rows for k in row))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")

def print_header(title):
    print("\n" + "=" * 76)
    print(title)
    print("=" * 76, flush=True)
