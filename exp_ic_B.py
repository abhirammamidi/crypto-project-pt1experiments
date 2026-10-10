"""Index-calculus smoothness-bound sweep for F/G.

Uses the actual index_calculus.solve implementation. Every row records the
seed, bound, relation count, rank, stage timings, verification, and exception.
Bounds are configurable; start with F because G's dense elimination is heavier.
"""
from __future__ import annotations
import argparse, time
from _setup import instance, verify, result_dir, write_csv, print_header
import index_calculus

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", default="F,G", help="comma-separated subset of F,G")
    ap.add_argument("--bounds", default="100,140,180,220,260",
                    help="comma-separated factor-base bounds")
    ap.add_argument("--relation-factor", type=float, default=2.0)
    ap.add_argument("--max-trials", type=int, default=500_000)
    ap.add_argument("--run-heavy", action="store_true",
                    help="allow G and larger bounds; otherwise G is skipped by default")
    args = ap.parse_args()
    labels = [x.strip() for x in args.instances.split(",") if x.strip()]
    bounds = [int(x.strip()) for x in args.bounds.split(",") if x.strip()]
    print_header("Experiment 4 — Index-calculus factor-base sweep")
    rows = []
    for label in labels:
        if label not in ("F", "G"):
            print(f"Skipping unsupported index-calculus instance {label}")
            continue
        if label == "G" and not args.run_heavy:
            print("Skipping G: pass --run-heavy to opt into heavier dense linear algebra.")
            continue
        inst = instance(label)
        for B in bounds:
            seed = 42000 + B + (1000 if label == "G" else 0)
            print(f"{label}: B={B}, seed={seed} starting...", flush=True)
            t0 = time.perf_counter()
            try:
                x, stats = index_calculus.solve(
                    inst["g"], inst["h"], inst["p"], inst["order"],
                    B=B, relation_factor=args.relation_factor,
                    seed=seed, max_trials=args.max_trials
                )
                wall = time.perf_counter() - t0
                ok = verify(inst, x)
                row = {"instance": label, "B": B, "seed": seed, "success": ok,
                       "x": x, "wall_time_sec": wall, **stats}
                print(f"  success={ok}, time={wall:.2f}s, factor_base={stats.get('factor_base_size')}, "
                      f"relations={stats.get('relations')}, rank={stats.get('rank')}", flush=True)
            except Exception as exc:
                row = {"instance": label, "B": B, "seed": seed, "success": False,
                       "wall_time_sec": time.perf_counter()-t0,
                       "error": f"{type(exc).__name__}: {exc}"}
                print(f"  FAILED after {row['wall_time_sec']:.2f}s: {row['error']}", flush=True)
            rows.append(row)
    out = result_dir() / "exp_ic_B.csv"
    write_csv(out, rows)
    print(f"CSV: {out}")
if __name__ == "__main__":
    main()
