"""Reproducible Pollard-rho seed experiment on C and C2.

Reports every run, verification, iteration count, restarts, mean/sample
standard deviation, and comparison to sqrt(pi*n/2). A failed seed is retained
as a failure rather than silently omitted from the dataset.
"""
from __future__ import annotations
import argparse, math, statistics, time
from _setup import instance, verify, result_dir, write_csv, print_header
import pollard_rho

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--max-restarts", type=int, default=100)
    args = ap.parse_args()
    if args.runs < 2:
        ap.error("--runs must be >= 2 to compute standard deviation")
    print_header("Experiment 3 — Pollard rho seeded runs")
    rows = []
    for label in ("C", "C2"):
        inst = instance(label)
        n = inst["order"]
        expected = math.sqrt(math.pi * n / 2)
        times, iterations = [], []
        print(f"\n{label}: order={n}, theoretical birthday estimate ≈ {expected:,.0f} steps")
        for i in range(args.runs):
            seed = 20261010 + i
            start = time.perf_counter()
            try:
                x, stats = pollard_rho.solve(
                    inst["g"], inst["h"], inst["p"], n,
                    seed=seed, max_restarts=args.max_restarts
                )
                wall = time.perf_counter() - start
                ok = verify(inst, x)
                row = {"instance": label, "run": i + 1, "seed": seed,
                       "success": ok, "x": x, "wall_time_sec": wall,
                       "reported_time_sec": stats.get("time_sec"),
                       "group_ops": stats.get("group_ops"),
                       "iterations": stats.get("iterations"),
                       "restarts": stats.get("restarts"),
                       "candidates_checked": stats.get("candidates_checked"),
                       "sqrt_order": math.sqrt(n), "birthday_estimate": expected}
                if ok:
                    times.append(wall)
                    iterations.append(stats.get("iterations", 0))
                rows.append(row)
                print(f"  run {i+1:02d}/{args.runs}: seed={seed} success={ok} "
                      f"time={wall:.4f}s iterations={stats.get('iterations')} "
                      f"restarts={stats.get('restarts')}", flush=True)
            except Exception as exc:
                rows.append({"instance": label, "run": i + 1, "seed": seed,
                             "success": False, "error": f"{type(exc).__name__}: {exc}"})
                print(f"  run {i+1:02d}: ERROR {type(exc).__name__}: {exc}", flush=True)
        print(f"  successful runs: {len(times)}/{args.runs}")
        if times:
            print(f"  wall-time mean={statistics.mean(times):.6f}s "
                  f"sample SD={statistics.stdev(times) if len(times)>1 else 0:.6f}s")
        if iterations:
            print(f"  iterations mean={statistics.mean(iterations):.1f} "
                  f"sample SD={statistics.stdev(iterations) if len(iterations)>1 else 0:.1f}")
    out = result_dir() / "exp_rho_runs.csv"
    write_csv(out, rows)
    print(f"\nCSV: {out}")
if __name__ == "__main__":
    main()
