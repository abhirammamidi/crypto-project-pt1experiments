"""Task 1.4: vary the smoothness bound B on instance F; plot stage times."""
import statistics
import _setup
import index_calculus

B_VALUES = [150, 250, 350, 500, 750, 1000, 1500]   # at least six values
REPEATS = 3                                         # relation collection is random
inst = _setup.instance("F")
rows = []
for B in B_VALUES:
    s1, s2, s3, tot = [], [], [], []
    for seed in range(REPEATS):
        x, st = index_calculus.solve(inst["g"], inst["h"], inst["p"], order=inst["order"],
                                     B=B, seed=seed)
        assert pow(inst["g"], x, inst["p"]) == inst["h"]
        s1.append(st["stage1_sec"]); s2.append(st["stage2_sec"])
        s3.append(st["stage3_sec"]); tot.append(st["time_sec"])
    med = [statistics.median(v) for v in (s1, s2, s3, tot)]
    rows.append([B, st["factor_base_size"]] + med)
    print(f"B={B:5d} L={st['factor_base_size']:4d} stage1={med[0]:.3f}s "
          f"stage2={med[1]:.3f}s stage3={med[2]:.3f}s total={med[3]:.3f}s")
_setup.write_csv("ic_B_experiment.csv", ["B", "L", "stage1_sec", "stage2_sec",
                 "stage3_sec", "total_sec"], rows)

plt = _setup.get_plt()
if plt:
    plt.figure(figsize=(6, 4))
    for col, name in ((2, "Stage 1 (relations)"), (3, "Stage 2 (linear algebra)"), (5, "Total")):
        plt.plot([r[0] for r in rows], [r[col] for r in rows], "o-", label=name)
    plt.xlabel("smoothness bound B")
    plt.ylabel("median time (s)")
    plt.title("Index calculus on F: time vs B")
    plt.legend()
    plt.tight_layout()
    plt.savefig(_setup.RESULTS + "/ic_B_experiment.png", dpi=200)
    print("wrote ic_B_experiment.png")
