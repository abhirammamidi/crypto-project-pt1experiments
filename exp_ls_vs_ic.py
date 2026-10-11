"""Task 1.5: linear sieve vs index calculus on G, with BOTH the assignment's starting
parameters and the ones stored in assignment_data.py. Failures are recorded as rows."""
import statistics
import _setup
import index_calculus
import linear_sieve
import params
from common import SolverFailure

REPEATS = 3
TIMEOUT = 300
inst = _setup.instance("G")
g, h, p, n = inst["g"], inst["h"], inst["p"], inst["order"]
configs = [
    (f"index_calculus B={params.IC_B['G']} (assignment)", lambda s: index_calculus.solve(g, h, p, order=n, B=params.IC_B["G"], seed=s, max_seconds=TIMEOUT)),
    (f"linear_sieve B={params.LS_B} M={params.LS_M} (assignment)", lambda s: linear_sieve.solve(g, h, p, order=n, B=params.LS_B, M=params.LS_M, seed=s, max_seconds=TIMEOUT)),
]
if inst.get("B_ic"):
    configs.append((f"index_calculus B={inst['B_ic']} (data file)", lambda s: index_calculus.solve(g, h, p, order=n, B=inst["B_ic"], seed=s, max_seconds=TIMEOUT)))
if inst.get("B_ls"):
    configs.append((f"linear_sieve B={inst['B_ls']} M={inst['M_ls']} (data file)", lambda s: linear_sieve.solve(g, h, p, order=n, B=inst["B_ls"], M=inst["M_ls"], seed=s, max_seconds=TIMEOUT)))
rows = []
for name, run in configs:
    per, last = {"stage1_sec": [], "stage2_sec": [], "stage3_sec": [], "time_sec": []}, None
    for seed in range(REPEATS):
        try:
            x, st = run(seed)
            assert pow(g, x, p) == h
            last = st
            for k in per:
                per[k].append(st[k])
        except SolverFailure as exc:
            print(f"{name} seed {seed}: FAILED ({exc})")
    if not per["time_sec"]:
        rows.append([name, "", "", "", "", "", "", "failed"])
        continue
    med = {k: statistics.median(v) for k, v in per.items()}
    note = f"ok; M {last['M_requested']}->{last['M_final']}" if "M_final" in last else "ok"
    rows.append([name, last["factor_base_size"], last["relations"], med["stage1_sec"],
                 med["stage2_sec"], med["stage3_sec"], med["time_sec"], note])
    print(f"{name}: unknowns={last['factor_base_size']} relations={last['relations']} "
          + " ".join(f"{k}={v:.3f}" for k, v in med.items()) + f"  [{note}]")
_setup.write_csv("ls_vs_ic.csv", ["method", "unknowns", "relations", "stage1_sec", "stage2_sec",
                 "stage3_sec", "total_sec", "status"], rows)

plt = _setup.get_plt()
ok = [r for r in rows if r[7] != "failed"]
if plt and ok:
    labels = [r[0].replace(" (", "\n(") for r in ok]
    s1, s2 = [r[3] for r in ok], [r[4] for r in ok]
    plt.figure(figsize=(8, 4.5))
    plt.bar(labels, s1, label="Stage 1 (relations)")
    plt.bar(labels, s2, bottom=s1, label="Stage 2 (linear algebra)")
    plt.ylabel("median time (s)")
    plt.title("Instance G: where the time goes")
    plt.xticks(fontsize=7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(_setup.RESULTS + "/ls_vs_ic.png", dpi=200)
    print("wrote ls_vs_ic.png")
