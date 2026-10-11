"""Task 1.3 scaling study: Pohlig-Hellman cost depends on the LARGEST PRIME FACTOR of the
group order, not on the size of p. Builds primes p of the same size whose p-1 has a
chosen largest prime factor q_max, and measures operations / time against sqrt(q_max)."""
import math
import random
import _setup
import pohlig_hellman
from common import is_probable_prime, primes_up_to, element_order

rng = random.Random(7)
SMALL = primes_up_to(60)[1:]                 # 3, 5, 7, ... (the 'smooth part' of the order)
TARGET_BITS = 80


def random_prime(bits):
    while True:
        c = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(c):
            return c


def build(qbits):
    """p = 2 * (small primes) * q + 1 with a q of `qbits` bits, p about TARGET_BITS bits."""
    q = random_prime(qbits)
    while True:
        m = 2
        while m * q < (1 << (TARGET_BITS - 1)):
            m *= rng.choice(SMALL)
        p = m * q + 1
        if is_probable_prime(p):
            return p, q


rows = []
for qbits in (12, 16, 20, 24, 28, 32, 36):
    p, q = build(qbits)
    factors = {}
    n = p - 1
    for r in SMALL + [2]:
        while n % r == 0:
            factors[r] = factors.get(r, 0) + 1
            n //= r
    assert n == q or n == 1 or is_probable_prime(n)
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    g = next(c for c in range(2, 200) if element_order(c, p, p - 1, factors) == p - 1)
    h = pow(g, rng.randrange(p - 1), p)
    x, st = pohlig_hellman.solve(g, h, p, order=p - 1, factors=factors)
    assert pow(g, x, p) == h
    rows.append([p.bit_length(), max(factors).bit_length(), math.isqrt(max(factors)),
                 st["group_ops"], st["inner_group_ops"], st["inner_peak_table"], st["time_sec"]])
    print(f"p {p.bit_length()} bits | q_max {max(factors).bit_length()} bits | sqrt(q_max)={math.isqrt(max(factors)):,} "
          f"| ops={st['group_ops']:,} (inner {st['inner_group_ops']:,}) | table={st['inner_peak_table']:,} | {st['time_sec']:.4f}s")
_setup.write_csv("ph_scaling.csv", ["p_bits", "qmax_bits", "sqrt_qmax", "group_ops",
                 "inner_group_ops", "inner_peak_table", "time_sec"], rows)

plt = _setup.get_plt()
if plt:
    xs = [r[2] for r in rows]
    plt.figure(figsize=(6, 4))
    plt.loglog(xs, [r[3] for r in rows], "o-", label="total group ops")
    plt.loglog(xs, [r[4] for r in rows], "s--", label="inner (BSGS) group ops")
    plt.xlabel("sqrt(largest prime factor)")
    plt.ylabel("group operations")
    plt.title(f"Pohlig-Hellman: cost vs largest prime factor (p ~ {TARGET_BITS} bits)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(_setup.RESULTS + "/ph_scaling.png", dpi=200)
    print("wrote ph_scaling.png")
