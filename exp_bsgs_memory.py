"""Task 1.1: BSGS peak table size vs sqrt(n) on >= 5 increasing toy instances."""
import math
import random
import tracemalloc
import _setup
import bsgs
from common import make_instance

BITS = [16, 20, 24, 28, 32, 36]
rng = random.Random(2026)
rows = []
for bits in BITS:
    g, h, p, n, x_true = make_instance(bits, rng)
    tracemalloc.start()
    x, st = bsgs.solve(g, h, p, order=n)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert x == x_true
    rows.append([bits, p, n, math.isqrt(n), st["memory_items"], peak_bytes,
                 peak_bytes / st["memory_items"], st["time_sec"]])
    print(f"{bits} bits: sqrt(n)={math.isqrt(n)} table={st['memory_items']} "
          f"peak={peak_bytes} B ({peak_bytes / st['memory_items']:.1f} B/entry)")
_setup.write_csv("bsgs_memory.csv", ["bits", "p", "n", "sqrt_n", "table_entries",
                 "peak_bytes", "bytes_per_entry", "time_sec"], rows)

plt = _setup.get_plt()
if plt:
    xs, ys = [r[3] for r in rows], [r[4] for r in rows]
    plt.figure(figsize=(6, 4))
    plt.plot(xs, ys, "o-", label="measured peak table size")
    plt.plot(xs, xs, "--", label="y = sqrt(n) (reference)")
    plt.xlabel("sqrt(n)")
    plt.ylabel("peak table entries")
    plt.title("BSGS memory vs sqrt(n)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(_setup.RESULTS + "/bsgs_memory.png", dpi=200)
    print("wrote bsgs_memory.png")

bpe = rows[-1][6]
m_max = 8 * 2**30 / bpe
print(f"8 GB estimate with {bpe:.1f} bytes/entry: m_max = {m_max:.3e}, "
      f"n_max = {m_max**2:.3e} = 2^{math.log2(m_max**2):.1f}")
