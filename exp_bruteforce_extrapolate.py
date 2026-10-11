"""Task 1.0: time brute force on A and B, extrapolate to D."""
import statistics
import _setup
import bruteforce

REPEATS = 5
SECONDS_PER_YEAR = 365.25 * 24 * 3600

rows, rates = [], []
for label in ("A", "B"):
    inst = _setup.instance(label)
    times = []
    for _ in range(REPEATS):
        x, st = bruteforce.solve(inst["g"], inst["h"], inst["p"], order=inst["order"])
        times.append(st["time_sec"])
    t = statistics.median(times)
    rate = t / max(st["group_ops"], 1)            # seconds per multiplication
    rates.append(rate)
    rows.append([label, inst["order"].bit_length(), x, st["group_ops"], t, rate])
    print(f"{label}: x={x} ops={st['group_ops']} median time={t:.6f}s  s/op={rate:.3e}")
_setup.write_csv("bruteforce_timings.csv",
                 ["instance", "order_bits", "x", "group_ops", "median_time_sec", "sec_per_op"], rows)

D = _setup.instance("D")
rate = statistics.mean(rates)
for name, ops in (("average case n/2", D["order"] / 2), ("worst case n", D["order"])):
    sec = rate * ops
    print(f"D {name}: {ops:.3e} ops -> {sec:.3e} s = {sec / SECONDS_PER_YEAR:.3e} years")
