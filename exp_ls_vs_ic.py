"""Compare index calculus and linear sieve on G with matched seed policy.

This is an actual algorithm comparison, not a claim that parameters are
identical in meaning: IC's B and linear-sieve B/M control different work.
Failures and rank-deficiency errors are kept in the CSV.
"""
from __future__ import annotations
import argparse, time
from _setup import instance, verify, result_dir, write_csv, print_header
import index_calculus, linear_sieve

def call_ic(inst, B, seed, max_trials):
    return index_calculus.solve(inst["g"], inst["h"], inst["p"], inst["order"],
                                B=B, seed=seed, max_trials=max_trials)

def call_ls(inst, B, M, seed):
    return linear_sieve.solve(inst["g"], inst["h"], inst["p"], inst["order"],
                              B=B, M=M, seed=seed)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", default="G", choices=["F", "G"])
    ap.add_argument("--ic-B", type=int, default=260)
    ap.add_argument("--ls-B", type=int, default=220)
    ap.add_argument("--ls-M", type=int, default=700)
    ap.add_argument("--max-trials", type=int, default=500_000)
    ap.add_argument("--run-heavy", action="store_true")
    args = ap.parse_args()
    if args.instance == "G" and not args.run_heavy:
        print("G uses heavier dense relation systems. Re-run with --run-heavy to proceed.")
        return
    inst = instance(args.instance)
    rows = []
    print_header(f"Experiment 5 — index calculus vs linear sieve on {args.instance}")
    for name, fn in (
        ("index_calculus", lambda: call_ic(inst, args.ic_B, 55101, args.max_trials)),
        ("linear_sieve", lambda: call_ls(inst, args.ls_B, args.ls_M, 55102)),
    ):
        print(f"{name}: starting...", flush=True)
        t0 = time.perf_counter()
        try:
            x, stats = fn()
            wall = time.perf_counter() - t0
            ok = verify(inst, x)
            row = {"instance": args.instance, "algorithm": name, "success": ok,
                   "x": x, "wall_time_sec": wall, **stats}
            print(f"  success={ok}, time={wall:.2f}s, ops={stats.get('group_ops')}, "
                  f"relations={stats.get('relations')}, rank={stats.get('rank')}", flush=True)
        except Exception as exc:
            row = {"instance": args.instance, "algorithm": name, "success": False,
                   "wall_time_sec": time.perf_counter()-t0,
                   "error": f"{type(exc).__name__}: {exc}"}
            print(f"  FAILED after {row['wall_time_sec']:.2f}s: {row['error']}", flush=True)
        rows.append(row)
    out = result_dir() / "exp_ls_vs_ic.csv"
    write_csv(out, rows)
    print(f"CSV: {out}")
if __name__ == "__main__":
    main()
