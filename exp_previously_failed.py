"""Re-runs every case that used to fail and prints a PASS/FAIL table (exit status 0 = all pass).

  * Index calculus F, B=100;  G, B=180;  G, B=220;  G (comparison)
  * Linear sieve G with the data-file parameters (B=220, M=700 -> used to give '31 rows for 748 unknowns')
  * Pollard rho C2: ten seeds must give independent walks (distinct iteration counts)
  * Pohlig-Hellman: group_ops now include the inner BSGS work
  * Brute force D: extrapolation (never run)
THIS REQUIRES assignment_data.py with instances C2, D, F, G (a case whose instance is missing is skipped)."""
import sys
import time
import _setup
import bruteforce
import index_calculus
import linear_sieve
import params
import pohlig_hellman
import pollard_rho
from common import SolverFailure

inst = _setup.all_instances()
rows, bad = [], 0


def record(name, fn):
    global bad
    t0 = time.perf_counter()
    try:
        ok, note = fn()
    except SolverFailure as exc:
        ok, note = False, f"controlled failure: {exc}"
    except Exception as exc:
        ok, note = False, f"{type(exc).__name__}: {exc}"
    bad += (not ok)
    rows.append([name, "PASS" if ok else "FAIL", f"{time.perf_counter() - t0:.2f}", note])
    print(f"{rows[-1][1]:<5} {name:<58} {rows[-1][2]:>8} s  {note}", flush=True)


def ic(label, B):
    def run():
        i = inst[label]
        x, st = index_calculus.solve(i["g"], i["h"], i["p"], order=i["order"], B=B, seed=0, max_seconds=600)
        return pow(i["g"], x, i["p"]) == i["h"], f"L={st['factor_base_size']} relations={st['relations']} rank={st['rank']}"
    return run


def ls(label, B, M):
    def run():
        i = inst[label]
        x, st = linear_sieve.solve(i["g"], i["h"], i["p"], order=i["order"], B=B, M=M, seed=0, max_seconds=600)
        return pow(i["g"], x, i["p"]) == i["h"], (f"unknowns={st['factor_base_size']} relations={st['relations']} "
                                                  f"M {st['M_requested']}->{st['M_final']}")
    return run


def rho_independence():
    i = inst["C2"]
    its = []
    for seed in range(10):
        x, st = pollard_rho.solve(i["g"], i["h"], i["p"], order=i["order"], seed=seed)
        assert pow(i["g"], x, i["p"]) == i["h"]
        its.append(st["iterations"])
    return len(set(its)) == len(its), f"{len(set(its))} distinct iteration counts out of {len(its)}"


def ph_counts():
    i = inst["D"]
    x, st = pohlig_hellman.solve(i["g"], i["h"], i["p"], order=i["order"], factors=i["factors"])
    ok = (pow(i["g"], x, i["p"]) == i["h"] and st["inner_group_ops"] > 0
          and st["group_ops"] == st["outer_group_ops"] + st["inner_group_ops"])
    return ok, f"outer {st['outer_group_ops']:,} + inner {st['inner_group_ops']:,} = {st['group_ops']:,}"


def bf_extrapolation():
    i = inst["D"]
    rate = bruteforce.calibrate(i["g"], i["p"])
    avg_s, _, avg_y, _ = bruteforce.extrapolate(rate, i["order"])
    return avg_y > 1, f"{rate:.2e} s/op on {i['p'].bit_length()}-bit numbers -> {avg_y:.3g} years on average (not run)"


if "F" in inst:
    record("Index calculus, F, B=100", ic("F", 100))
if "G" in inst:
    record("Index calculus, G, B=180", ic("G", 180))
    record("Index calculus, G, B=220", ic("G", 220))
    record(f"Index calculus, G, B={params.IC_B['G']} (comparison)", ic("G", params.IC_B["G"]))
    record(f"Linear sieve, G, B={params.LS_B} M={params.LS_M} (comparison)", ls("G", params.LS_B, params.LS_M))
    record("Linear sieve, G, B=220 M=700 (old data-file values)", ls("G", 220, 700))
if "C2" in inst:
    record("Pollard rho, C2, 10 seeds are independent", rho_independence)
if "D" in inst:
    record("Pohlig-Hellman, D, group_ops include inner BSGS", ph_counts)
    record("Brute force, D, extrapolated (not run)", bf_extrapolation)
print(f"\n{len(rows) - bad}/{len(rows)} cases pass")
sys.exit(1 if bad else 0)
