"""BSGS runtime/memory scaling on real assignment instances and generated toys.

Timing and tracemalloc memory are measured in separate runs because tracing
allocation changes runtime. Generated cases use a fixed seed and are clearly
labelled; they never overwrite assignment_data.py.
"""
from __future__ import annotations
import argparse, math, random, time, tracemalloc
from _setup import instance, verify, result_dir, write_csv, print_header
import bsgs
from common import random_safe_prime, safe_prime_generator

def measure(inst, label):
    args = (inst["g"], inst["h"], inst["p"], inst["order"])
    t0 = time.perf_counter()
    x, stats = bsgs.solve(*args)
    elapsed = time.perf_counter() - t0
    tracemalloc.start()
    try:
        x_mem, _ = bsgs.solve(*args)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    ok = verify(inst, x) and x == x_mem
    return {"instance": label, "p_bits": inst["p"].bit_length(),
            "order": inst["order"], "sqrt_order": math.sqrt(inst["order"]),
            "x": x, "verified": ok, "time_sec": elapsed,
            "reported_group_ops": stats.get("group_ops"),
            "reported_memory_items": stats.get("memory_items"),
            "tracemalloc_peak_bytes": peak}

def generated(bits, seed):
    rng = random.Random(seed)
    p = random_safe_prime(bits, rng)
    g = safe_prime_generator(p)
    order = p - 1
    x = rng.randrange(order)
    return {"p": p, "g": g, "h": pow(g, x, p), "order": order}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated", action="store_true",
                    help="also generate reproducible 18/20/22-bit safe-prime toy cases")
    ap.add_argument("--include-c", action="store_true",
                    help="include C (can consume substantial memory)")
    args = ap.parse_args()
    print_header("Experiment 2 — BSGS time/memory scaling")
    labels = ["A", "B"] + (["C"] if args.include_c else [])
    rows = []
    for label in labels:
        print(f"Running BSGS on {label}...", flush=True)
        row = measure(instance(label), label)
        rows.append(row)
        print(f"  verified={row['verified']} time={row['time_sec']:.4f}s "
              f"peak={row['tracemalloc_peak_bytes'] / 1024:.1f} KiB "
              f"table_items={row['reported_memory_items']}")
    if args.generated:
        for bits in (18, 20, 22):
            label = f"generated_{bits}bit_seed_20261010"
            inst = generated(bits, 20261010 + bits)
            print(f"Running generated {bits}-bit case...", flush=True)
            row = measure(inst, label)
            rows.append(row)
            print(f"  verified={row['verified']} time={row['time_sec']:.4f}s")
    out = result_dir() / "exp_bsgs_memory.csv"
    write_csv(out, rows)
    print(f"CSV: {out}")
if __name__ == "__main__":
    main()
