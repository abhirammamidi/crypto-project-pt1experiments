"""One entry point for the experiment suite.

Quick-safe defaults:
    python -m experiments.run_experiments --quick

Full suite:
    python -m experiments.run_experiments --full
Heavy index-calculus/linear-sieve runs are opt-in because dense Gaussian
elimination can exceed several minutes on larger factor bases.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(args):
    print("\n>>>", " ".join(args), flush=True)
    return subprocess.run(args, cwd=ROOT, check=False).returncode

def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--quick", action="store_true")
    group.add_argument("--full", action="store_true")
    args = ap.parse_args()
    py = sys.executable
    jobs = [
        [py, str(ROOT/"experiments"/"exp_bruteforce_extrapolate.py")],
        [py, str(ROOT/"experiments"/"exp_bsgs_memory.py"), "--generated"],
        [py, str(ROOT/"experiments"/"exp_rho_runs.py"), "--runs", "10"],
        [py, str(ROOT/"experiments"/"exp_ic_B.py")],
        [py, str(ROOT/"experiments"/"exp_ls_vs_ic.py")],
    ]
    if args.full:
        jobs[1] = [py, str(ROOT/"experiments"/"exp_bsgs_memory.py"), "--generated", "--include-c"]
        jobs[3] += ["--run-heavy"]
        jobs[4] += ["--run-heavy"]
    codes = []
    for job in jobs:
        code = run(job)
        codes.append((job[-1], code))
        if code:
            print(f"WARNING: process exited with code {code}; continuing.", flush=True)
    print("\nExperiment suite complete. Check the results/ directory.")
    print("Non-zero subprocess codes:", [x for x in codes if x[1]])
if __name__ == "__main__":
    main()
