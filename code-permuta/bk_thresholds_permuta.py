#!/usr/bin/env python3
"""README

permuta-based reimplementation of the exact threshold data N_k for the
monotone-forcing sets B_k.

How to run:
  python \
    code-permuta/bk_thresholds_permuta.py 5 20
  python \
    code-permuta/bk_thresholds_permuta.py all

Notes:
- On this machine the permuta approach is very fast for k <= 5.
- The k=6 computation appears substantially slower, so this script has a
  runtime guard and will stop rather than pretending to be routine.
"""

from __future__ import annotations

import argparse
from time import perf_counter
from permuta import Av, Perm


def build_b_k(k: int):
    if not (3 <= k <= 9):
        raise ValueError("expected 3 <= k <= 9")

    p = list(range(1, k - 1)) + [k, k - 1]
    q = [1] + list(range(k, 1, -1))
    r = [2, 1] + list(range(3, k + 1))
    s = list(range(2, k + 1)) + [1]

    return sorted({
        Perm.to_standard(tuple(p)),
        Perm.to_standard(tuple(q)),
        Perm.to_standard(tuple(r)),
        Perm.to_standard(tuple(s)),
        Perm.to_standard(tuple(p)).complement(),
        Perm.to_standard(tuple(q)).complement(),
        Perm.to_standard(tuple(r)).complement(),
        Perm.to_standard(tuple(s)).complement(),
    })


def run_case(k: int, max_n: int, max_seconds_per_count: float) -> None:
    basis = build_b_k(k)
    cls = Av(basis)
    counts = []
    cutoff = None

    print(f"k={k} B_k={{{','.join(str(p) for p in basis)}}}")
    for n in range(max_n + 1):
        t0 = perf_counter()
        count = cls.count(n)
        elapsed = perf_counter() - t0
        counts.append(count)
        print(f"n={n} count={count}")
        if elapsed > max_seconds_per_count:
            cutoff = (n, elapsed)
            break

    threshold = None
    if cutoff is None:
        for n in range(k, len(counts)):
            if counts[n] == 2 and all(c == 2 for c in counts[n:]):
                threshold = n
                break

    if threshold is not None:
        print(f"first_n_with_only_monotones={threshold}")
    elif cutoff is not None:
        n, elapsed = cutoff
        print(
            "first_n_with_only_monotones="
            f"not_found_before_runtime_guard_at_n={n}_elapsed={elapsed:.3f}s"
        )
    else:
        print(f"first_n_with_only_monotones=not_found_up_to_{max_n}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("k_or_all", help="either 'all' or a single value of k")
    parser.add_argument("max_n", nargs="?", type=int, help="largest n to test")
    parser.add_argument(
        "--max-seconds-per-count",
        type=float,
        default=10.0,
        help="stop a run if one cls.count(n) call exceeds this many seconds",
    )
    args = parser.parse_args()

    if args.k_or_all == "all":
        for k, max_n in [(3, 6), (4, 10), (5, 20), (6, 30)]:
            run_case(k, max_n, args.max_seconds_per_count)
        return 0

    if args.max_n is None:
        parser.error("max_n is required unless the first argument is 'all'")
    run_case(int(args.k_or_all), args.max_n, args.max_seconds_per_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
