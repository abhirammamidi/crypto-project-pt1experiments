"""Task 1.4: vary the smoothness bound B on instance F; plot stage times.
    python exp_ic_B.py [--instances F] [--bounds 100,150,...] [--repeats 3] [--timeout 300]
A B that fails (budget/rank) is recorded as a failed row, not hidden and not substituted."""
import argparse
import statistics
import _setup
import index_calculus
from common import SolverFailure

ap = argparse.ArgumentParser()
ap.add_argument("--instances", default="F")
ap.add_argument("--bounds", default="100,150,200,300,450,700,1000,1500")
ap.add_argument("--repeats", type=int, default=3)
ap.add_argument("--max-trials", type=int, default=None)
ap.add_argument("--timeout", type=float, default=300)
args = ap.parse_args()

for label in args.instances.split(","):
    inst = _setup.instance(label)
    rows = []
    for B in [int(b) for b in args.bounds.split(",")]:
        runs = []
        for seed in range(args.repeats):
            try:
                x, st = index_calculus.solve(inst["g"], inst["h"], inst["p"], order=inst["order"], B=B,
                                             seed=seed, max_trials=args.max_trials, max_seconds=args.timeout)
                assert pow(inst["g"], x, inst["p"]) == inst["h"]
                runs.append(st)
            except SolverFailure as exc:
                print(f"{label} B={B} seed {seed}: FAILED ({exc})")
        if not runs:
            rows.append([B, "", "", "", "", "", "failed"])
            continue
        med = {k: statistics.median(r[k] for r in runs) for k in ("stage1_sec", "stage2_sec", "stage3_sec", "time_sec")}
        rows.append([B, runs[0]["factor_base_size"], med["stage1_sec"], med["stage2_sec"],
                     med["stage3_sec"], med["time_sec"], f"ok {len(runs)}/{args.repeats}"])
        print(f"{label} B={B:5d} L={runs[0]['factor_base_size']:4d} stage1={med['stage1_sec']:.3f}s "
              f"stage2={med['stage2_sec']:.3f}s stage3={med['stage3_sec']:.3f}s total={med['time_sec']:.3f}s")
    _setup.write_csv(f"ic_B_experiment_{label}.csv",
                     ["B", "L", "stage1_sec", "stage2_sec", "stage3_sec", "total_sec", "status"], rows)
    plt = _setup.get_plt()
    ok = [r for r in rows if r[6] != "failed"]
    if plt and ok:
        plt.figure(figsize=(6, 4))
        for col, name in ((2, "Stage 1 (relations)"), (3, "Stage 2 (linear algebra)"), (5, "Total")):
            plt.plot([r[0] for r in ok], [r[col] for r in ok], "o-", label=name)
        plt.xlabel("smoothness bound B")
        plt.ylabel("median time (s)")
        plt.title(f"Index calculus on {label}: time vs B")
        plt.legend()
        plt.tight_layout()
        plt.savefig(_setup.RESULTS + f"/ic_B_experiment_{label}.png", dpi=200)
        print(f"wrote ic_B_experiment_{label}.png")
