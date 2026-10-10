"""Brute-force baseline: measured A/B and transparent extrapolation to D.

Brute-force runs are capped by --max-seconds. Extrapolation uses observed
modular-multiplication throughput and reports assumptions rather than
pretending the 116-bit instance was actually solved.
"""
from __future__ import annotations
import argparse, time, math
from _setup import instance, verify, result_dir, write_csv, print_header
import bruteforce

def run_one(label, max_seconds):
    inst = instance(label)
    start = time.perf_counter()
    # Run the actual solver only for instances within the user's time budget.
    # Python's synchronous call cannot be interrupted safely, so pre-estimate
    # with a short throughput calibration first.
    calibration_n = min(200_000, inst["order"])
    cur = 1
    t0 = time.perf_counter()
    for _ in range(calibration_n):
        cur = cur * inst["g"] % inst["p"]
    dt = max(time.perf_counter() - t0, 1e-9)
    ops_per_sec = calibration_n / dt
    estimated_ops = inst["order"] / 2
    estimate_sec = estimated_ops / ops_per_sec
    if estimate_sec > max_seconds:
        print(f"{label}: SKIPPED actual solve; estimated median work {estimate_sec:.2f}s "
              f"> budget {max_seconds:.2f}s; calibration {ops_per_sec:,.0f} mul/s")
        return {
            "instance": label, "status": "skipped_by_budget", "estimate_sec": estimate_sec,
            "calibration_ops_per_sec": ops_per_sec, "group_ops": "", "time_sec": "",
            "verified": "", "x": ""
        }
    print(f"{label}: running solver (estimated {estimate_sec:.2f}s)...", flush=True)
    x, stats = bruteforce.solve(inst["g"], inst["h"], inst["p"], inst["order"])
    ok = verify(inst, x)
    row = {"instance": label, "status": "solved" if ok else "failed",
           "estimate_sec": estimate_sec, "calibration_ops_per_sec": ops_per_sec,
           "group_ops": stats.get("group_ops"), "time_sec": stats.get("time_sec"),
           "verified": ok, "x": x}
    print(f"  x={x}, verified={ok}, ops={stats.get('group_ops')}, time={stats.get('time_sec'):.4f}s")
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-seconds", type=float, default=15.0,
                    help="skip real brute-force runs whose calibrated estimate exceeds this")
    args = ap.parse_args()
    print_header("Experiment 1 — brute-force baseline and D extrapolation")
    rows = [run_one(k, args.max_seconds) for k in ("A", "B")]
    # Calibrate independently against D's modulus and generator; throughput is
    # an approximate Python integer-modular multiplication rate.
    d = instance("D")
    reps = 200_000
    cur, t0 = 1, time.perf_counter()
    for _ in range(reps):
        cur = cur * d["g"] % d["p"]
    elapsed = max(time.perf_counter() - t0, 1e-9)
    rate = reps / elapsed
    expected_ops = d["order"] / 2
    seconds = expected_ops / rate
    years = seconds / (365.25 * 24 * 3600)
    print(f"\nD extrapolation (NOT an actual solve):")
    print(f"  calibration: {rate:,.0f} modular multiplications/s")
    print(f"  expected trial multiplications: {expected_ops:.4e}")
    print(f"  estimated time: {seconds:.4e} seconds = {years:.4e} years")
    rows.append({"instance": "D", "status": "extrapolated_not_run",
                 "estimate_sec": seconds, "calibration_ops_per_sec": rate,
                 "group_ops": expected_ops, "time_sec": "", "verified": "", "x": ""})
    out = result_dir() / "exp_bruteforce.csv"
    write_csv(out, rows)
    print(f"\nCSV: {out}")
if __name__ == "__main__":
    main()
