"""Task 1.0: time brute force on A and B, extrapolate to D (never run on D)."""
import statistics
import _setup
import bruteforce

REPEATS = 5
rows, rates = [], []
for label in ("A", "B"):
    inst = _setup.instance(label)
    times = []
    for _ in range(REPEATS):
        x, st = bruteforce.solve(inst["g"], inst["h"], inst["p"], order=inst["order"])
        times.append(st["time_sec"])
    t = statistics.median(times)
    rate = t / max(st["group_ops"], 1)
    rates.append(rate)
    rows.append([label, inst["order"].bit_length(), x, st["group_ops"], t, rate])
    print(f"{label}: x={x} ops={st['group_ops']} median time={t:.6f}s  s/op={rate:.3e}")
ra, rb = rows[0], rows[1]
print(f"linearity check: time(B)/time(A) = {rb[4] / ra[4]:.2f}  vs ops(B)/ops(A) = {rb[3] / ra[3]:.2f}")

D = _setup.instance("D")
print(f"\nD: order has {D['order'].bit_length()} bits")
cal = bruteforce.calibrate(D["g"], D["p"])          # bounded partial run at D's number size
print(f"measured on D-sized numbers (300,000 multiplications): {cal:.3e} s/op")
out = []
for name, rate in (("rate from A,B (mean)", statistics.mean(rates)), ("rate calibrated on D", cal)):
    avg_s, worst_s, avg_y, worst_y = bruteforce.extrapolate(rate, D["order"])
    print(f"{name}: average {avg_s:.3e} s = {avg_y:.3e} years; worst case {worst_y:.3e} years")
    out.append([name, rate, avg_s, avg_y, worst_s, worst_y])
_setup.write_csv("bruteforce_timings.csv",
                 ["instance", "order_bits", "x", "group_ops", "median_time_sec", "sec_per_op"], rows)
_setup.write_csv("bruteforce_extrapolation_D.csv",
                 ["rate_source", "sec_per_op", "avg_sec", "avg_years", "worst_sec", "worst_years"], out)
