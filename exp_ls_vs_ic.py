"""Task 1.5: linear sieve (B=700, M=900) vs index calculus (B=2000) on G."""
import statistics
import _setup
import index_calculus
import linear_sieve

REPEATS = 3
inst = _setup.instance("G")
configs = [
    ("index_calculus B=2000", lambda s: index_calculus.solve(
        inst["g"], inst["h"], inst["p"], order=inst["order"], B=2000, seed=s)),
    ("linear_sieve B=700 M=900", lambda s: linear_sieve.solve(
        inst["g"], inst["h"], inst["p"], order=inst["order"], B=700, M=900, seed=s)),
]
rows = []
for name, run in configs:
    per = {"stage1_sec": [], "stage2_sec": [], "stage3_sec": [], "time_sec": []}
    for seed in range(REPEATS):
        x, st = run(seed)
        assert pow(inst["g"], x, inst["p"]) == inst["h"]
        for k in per:
            per[k].append(st[k])
    med = {k: statistics.median(v) for k, v in per.items()}
    rows.append([name, st["factor_base_size"], st["relations"], med["stage1_sec"],
                 med["stage2_sec"], med["stage3_sec"], med["time_sec"]])
    print(f"{name}: unknowns={st['factor_base_size']} relations={st['relations']} "
          + " ".join(f"{k}={v:.3f}" for k, v in med.items()))
_setup.write_csv("ls_vs_ic.csv", ["method", "unknowns", "relations", "stage1_sec",
                 "stage2_sec", "stage3_sec", "total_sec"], rows)

plt = _setup.get_plt()
if plt:
    labels = [r[0] for r in rows]
    s1 = [r[3] for r in rows]
    s2 = [r[4] for r in rows]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, s1, label="Stage 1 (relations)")
    plt.bar(labels, s2, bottom=s1, label="Stage 2 (linear algebra)")
    plt.ylabel("median time (s)")
    plt.title("Instance G: where the time goes")
    plt.legend()
    plt.tight_layout()
    plt.savefig(_setup.RESULTS + "/ls_vs_ic.png", dpi=200)
    print("wrote ls_vs_ic.png")
