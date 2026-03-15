#!/usr/bin/env python3
"""README

permuta-based reimplementation of the exact k=5 full-space computations used in
the main paper.

What it checks at n=8:
- the one-companion count in the general-k discussion;
- the full-space reverse-pair separation count in the conclusion.

How to run:
  python \
    code-permuta/k5_fullspace_data_permuta.py all

The runs during development used Python 3.11 with permuta.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import sys

from permuta import Perm


def pattern_shadow(perm: Perm, k: int):
    return {
        Perm.to_standard(tuple(perm[i] for i in positions))
        for positions in combinations(range(len(perm)), k)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["all", "companions", "separation"],
        help="Which exact k=5 computation to run.",
    )
    args = parser.parse_args()

    inc = Perm.to_standard("12345")
    dec = Perm.to_standard("54321")
    b5 = {Perm.to_standard(s) for s in (
        "12354", "15432", "21345", "23451",
        "43215", "45321", "51234", "54312",
    )}

    one_companion_targets = set()
    separable_pairs = set()

    errors = 0
    for perm in Perm.of_length(8):
        shadow = pattern_shadow(perm, 5)
        shadow.discard(inc)
        shadow.discard(dec)

        if args.command in {"all", "companions"} and len(shadow) == 2:
            a, b = tuple(shadow)
            a_in_b5 = a in b5
            b_in_b5 = b in b5
            if a_in_b5 != b_in_b5:
                one_companion_targets.add(b if a_in_b5 else a)

        if args.command in {"all", "separation"}:
            for patt in shadow:
                mate = patt.reverse()
                if mate not in shadow:
                    separable_pairs.add(min(patt, mate))

    if args.command in {"all", "companions"}:
        targets = ",".join(sorted(str(p) for p in one_companion_targets))
        print(f"one_companion_targets={len(one_companion_targets)} total_nonB5_nonmonotone=110")
        print(f"one_companion_target_list={targets}")
        if len(one_companion_targets) != 28:
            print("unexpected one-companion target count", file=sys.stderr)
            errors += 1

    if args.command in {"all", "separation"}:
        print(f"full_space_separable_pairs={len(separable_pairs)} total_nonmonotone_pairs=59")
        print("inseparable_pairs=none" if len(separable_pairs) == 59 else "inseparable_pairs=some")
        if len(separable_pairs) != 59:
            print("unexpected full-space separable pair count", file=sys.stderr)
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
