"""Task 1.2: Pollard rho, 10 seeds per instance (C and C2), plus BSGS on C."""
import math
import statistics
import _setup
import bsgs
import pollard_rho

SEEDS = range(10)
rows = []
for label in ("C", "C2"):
    inst = _setup.instance(label)
    n = inst["order"]
    times, ops, iters, restarts = [], [], [], []
    for seed in SEEDS:
        x, st = pollard_rho.solve(inst["g"], inst["h"], inst["p"], order=n, seed=seed)
        assert pow(inst["g"], x, inst["p"]) == inst["h"]
        times.append(st["time_sec"]); ops.append(st["group_ops"])
        iters.append(st["iterations"]); restarts.append(st["restarts"])
        rows.append([label, seed, x, st["time_sec"], st["group_ops"], st["iterations"], st["restarts"]])
    root = math.sqrt(n)
    print(f"\n{label}: sqrt(n) = {root:.3e}")
    print(f"  time   mean {statistics.mean(times):.4f} s   sd {statistics.stdev(times):.4f} s")
    print(f"  ops    mean {statistics.mean(ops):.3e}   ops/sqrt(n) = {statistics.mean(ops) / root:.3f}")
    print(f"  iters  mean {statistics.mean(iters):.3e}   iters/sqrt(n) = {statistics.mean(iters) / root:.3f}")
    print(f"  compare with 1.25*sqrt(n) = {1.25 * root:.3e};  total restarts = {sum(restarts)}")
_setup.write_csv("rho_runs.csv", ["instance", "seed", "x", "time_sec", "group_ops",
                 "iterations", "restarts"], rows)

inst = _setup.instance("C")
x, st = bsgs.solve(inst["g"], inst["h"], inst["p"], order=inst["order"])
print(f"\nBSGS on C: time {st['time_sec']:.4f} s  ops {st['group_ops']}  "
      f"table entries {st['memory_items']}")
_setup.write_csv("bsgs_on_C.csv", ["time_sec", "group_ops", "memory_items"],
                 [[st["time_sec"], st["group_ops"], st["memory_items"]]])
