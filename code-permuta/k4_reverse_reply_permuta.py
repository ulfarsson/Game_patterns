#!/usr/bin/env python3
"""README

permuta-based reimplementation of the exact k=4 computations used in Section 6
of the paper.

What it checks:
- the explicit extended witness families;
- the exact residual n=7 state classification for the non-hard gap cases;
- the hard-pair computation.

How to run:
  python \
    code-permuta/k4_reverse_reply_permuta.py all
"""

from __future__ import annotations

import argparse
from itertools import combinations
import sys

from permuta import Perm


def pat4_set(perm) -> set[Perm]:
    return {
        Perm.to_standard(tuple(perm[i] for i in positions))
        for positions in combinations(range(len(perm)), 4)
    }


MONOTONE = {Perm.monotone_increasing(4), Perm.monotone_decreasing(4)}
B4 = {
    Perm.to_standard("1243"), Perm.to_standard("1432"), Perm.to_standard("2134"), Perm.to_standard("2341"),
    Perm.to_standard("3214"), Perm.to_standard("3421"), Perm.to_standard("4123"), Perm.to_standard("4312"),
}
HARD_A = Perm.to_standard("2413")
HARD_B = Perm.to_standard("3142")


def as_perm(token: str) -> Perm:
    return Perm.to_standard(token)


EXTENDED_WITNESSES = {
    as_perm("1324"): [
        (as_perm("1243"), lambda n: tuple(list(range(1, n - 2)) + [n - 1, n - 2, n])),
        (as_perm("2134"), lambda n: tuple([1, 3, 2] + list(range(4, n + 1)))),
    ],
    as_perm("1342"): [
        (as_perm("1243"), lambda n: tuple(list(range(1, n - 2)) + [n - 1, n, n - 2])),
        (as_perm("2341"), lambda n: tuple([1] + list(range(3, n + 1)) + [2])),
    ],
    as_perm("1423"): [
        (as_perm("1243"), lambda n: tuple(list(range(1, n - 2)) + [n, n - 2, n - 1])),
        (as_perm("4123"), lambda n: tuple([1, n] + list(range(2, n)))),
    ],
    as_perm("2143"): [
        (as_perm("1432"), lambda n: tuple([2, 1] + list(range(n, 2, -1)))),
        (as_perm("3214"), lambda n: tuple(list(range(n - 2, 0, -1)) + [n, n - 1])),
    ],
    as_perm("2314"): [
        (as_perm("2134"), lambda n: tuple([2, 3, 1] + list(range(4, n + 1)))),
        (as_perm("2341"), lambda n: tuple(list(range(2, n)) + [1, n])),
    ],
    as_perm("2431"): [
        (as_perm("1432"), lambda n: tuple([2] + list(range(n, 2, -1)) + [1])),
        (as_perm("3421"), lambda n: tuple([n - 2, n, n - 1] + list(range(n - 3, 0, -1)))),
    ],
    as_perm("3124"): [
        (as_perm("2134"), lambda n: tuple([3, 1, 2] + list(range(4, n + 1)))),
        (as_perm("4123"), lambda n: tuple([n - 1] + list(range(1, n - 1)) + [n])),
    ],
    as_perm("3241"): [
        (as_perm("3214"), lambda n: tuple(list(range(n - 1, 1, -1)) + [n, 1])),
        (as_perm("3421"), lambda n: tuple([n - 1, n - 2, n] + list(range(n - 3, 0, -1)))),
    ],
    as_perm("3412"): [
        (as_perm("2341"), lambda n: tuple(list(range(3, n + 1)) + [1, 2])),
        (as_perm("4123"), lambda n: tuple([n - 1, n] + list(range(1, n - 1)))),
    ],
    as_perm("4132"): [
        (as_perm("1432"), lambda n: tuple([n, 1] + list(range(n - 1, 1, -1)))),
        (as_perm("4312"), lambda n: tuple(list(range(n, 3, -1)) + [1, 3, 2])),
    ],
    as_perm("4213"): [
        (as_perm("3214"), lambda n: tuple([n] + list(range(n - 2, 0, -1)) + [n - 1])),
        (as_perm("4312"), lambda n: tuple(list(range(n, 3, -1)) + [2, 1, 3])),
    ],
    as_perm("4231"): [
        (as_perm("3421"), lambda n: tuple([n, n - 2, n - 1] + list(range(n - 3, 0, -1)))),
        (as_perm("4312"), lambda n: tuple(list(range(n, 3, -1)) + [2, 3, 1])),
    ],
}


NONMONOTONE_REVERSE_PAIRS = []
seen = set()
for patt in Perm.of_length(4):
    if patt in MONOTONE or patt in seen:
        continue
    mate = patt.reverse()
    NONMONOTONE_REVERSE_PAIRS.append((min(patt, mate), max(patt, mate)))
    seen.add(patt)
    seen.add(mate)
NONMONOTONE_REVERSE_PAIRS.sort()
PAIR_INDEX = {pair: idx for idx, pair in enumerate(NONMONOTONE_REVERSE_PAIRS)}


def inflate_single_entry(base: Perm, entry_index: int, block_size: int, increasing: bool):
    components = [None] * len(base)
    if increasing:
        components[entry_index] = Perm.monotone_increasing(block_size)
    else:
        components[entry_index] = Perm.monotone_decreasing(block_size)
    return base.inflate(components)


def stable_oneblock_support(base: Perm, entry_index: int, increasing: bool) -> set[Perm]:
    support = set()
    for block_size in range(1, 5):
        support |= pat4_set(inflate_single_entry(base, entry_index, block_size, increasing))
    return support - MONOTONE


def reverse_pair_mask(patterns: set[Perm]) -> int:
    mask = 0
    for pattern in patterns:
        pair = (min(pattern, pattern.reverse()), max(pattern, pattern.reverse()))
        mask |= 1 << PAIR_INDEX[pair]
    return mask


def external_hard_pair_mask(patterns: set[Perm]) -> int:
    return reverse_pair_mask(patterns - {HARD_A, HARD_B})


def gap_case_reply_support_masks():
    masks = {target: set() for target in EXTENDED_WITNESSES}
    for base in Perm.of_length(6):
        for entry_index in range(6):
            for increasing in (False, True):
                support = stable_oneblock_support(base, entry_index, increasing)
                for target in EXTENDED_WITNESSES:
                    target_reverse = target.reverse()
                    if target_reverse not in support or target in support:
                        continue
                    masks[target].add(reverse_pair_mask(support - {target, target_reverse}))
    return masks


def verify_extended_witnesses(max_n: int = 20) -> int:
    errors = 0
    checked = 0
    for target, families in sorted(EXTENDED_WITNESSES.items(), key=lambda item: tuple(item[0])):
        target_reverse = target.reverse()
        for companion, builder in families:
            for n in range(7, max_n + 1):
                perm = builder(n)
                nonmonotone_shadow = pat4_set(perm) - MONOTONE
                if nonmonotone_shadow != {target, companion}:
                    print(
                        "FAIL wrong non-monotone shadow:",
                        f"target={target}",
                        f"companion={companion}",
                        f"n={n}",
                        file=sys.stderr,
                    )
                    errors += 1
                if target_reverse in nonmonotone_shadow:
                    print(
                        "FAIL reverse appears in witness:",
                        f"target={target}",
                        f"companion={companion}",
                        f"n={n}",
                        file=sys.stderr,
                    )
                    errors += 1
                checked += 1
    if errors == 0:
        print(f"extended_witnesses ok checks={checked}")
    return errors


def verify_gap_cases() -> int:
    permutations = list(Perm.of_length(7))
    shadow = {perm: pat4_set(perm) for perm in permutations}
    reply_support_masks = gap_case_reply_support_masks()

    b4_pairs = [
        frozenset({as_perm("1243"), as_perm("3421")}),
        frozenset({as_perm("1432"), as_perm("2341")}),
        frozenset({as_perm("2134"), as_perm("4312")}),
        frozenset({as_perm("3214"), as_perm("4123")}),
    ]

    companion_indices = {}
    for target, families in EXTENDED_WITNESSES.items():
        indices = set()
        for companion, _ in families:
            for index, pair in enumerate(b4_pairs):
                if companion in pair:
                    indices.add(index)
        companion_indices[target] = indices

    errors = 0
    checked = 0
    for mask in range(1 << len(NONMONOTONE_REVERSE_PAIRS)):
        forbidden = set()
        for i, pair in enumerate(NONMONOTONE_REVERSE_PAIRS):
            if mask & (1 << i):
                forbidden.update(pair)

        present_b4_pairs = {index for index, pair in enumerate(b4_pairs) if pair <= forbidden}
        if len(present_b4_pairs) == 4:
            continue

        avoiders = [perm for perm in permutations if not (shadow[perm] & forbidden)]
        if not avoiders:
            continue

        for target in EXTENDED_WITNESSES:
            if target in forbidden or target in {HARD_A, HARD_B}:
                continue
            if not (companion_indices[target] <= present_b4_pairs):
                continue
            if not any(target in shadow[perm] for perm in avoiders):
                continue

            checked += 1
            if not any((mask & support_mask) == 0 for support_mask in reply_support_masks[target]):
                print(f"FAIL gap case target={target}", file=sys.stderr)
                errors += 1

    if errors == 0:
        print(f"gap_cases ok checks={checked}")
    return errors


def verify_hard_pair() -> int:
    support_from_a = set()
    support_from_b = set()
    for base in Perm.of_length(6):
        for entry_index in range(6):
            for increasing in (False, True):
                support = stable_oneblock_support(base, entry_index, increasing)
                if HARD_A in support and HARD_B not in support:
                    support_from_a.add(external_hard_pair_mask(support))
                if HARD_B in support and HARD_A not in support:
                    support_from_b.add(external_hard_pair_mask(support))

    errors = 0
    if support_from_a != support_from_b:
        print("FAIL hard pair support sets do not match", file=sys.stderr)
        errors += 1
    if len(support_from_a) != 138:
        print(f"FAIL hard pair support count={len(support_from_a)} expected=138", file=sys.stderr)
        errors += 1

    permutations = list(Perm.of_length(7))
    shadows = [pat4_set(perm) for perm in permutations]
    legal_states = 0
    uncovered = 0
    for mask in range(1 << len(NONMONOTONE_REVERSE_PAIRS)):
        forbidden = set()
        for i, pair in enumerate(NONMONOTONE_REVERSE_PAIRS):
            if mask & (1 << i):
                forbidden.update(pair)
        if HARD_A in forbidden or HARD_B in forbidden:
            continue

        move_legal = any(HARD_A in perm_shadow and not (perm_shadow & forbidden) for perm_shadow in shadows)
        if not move_legal:
            continue

        legal_states += 1
        if all(mask & support_mask for support_mask in support_from_a):
            uncovered += 1

    if legal_states != 543:
        print(f"FAIL hard pair legal state count={legal_states} expected=543", file=sys.stderr)
        errors += 1
    if uncovered != 0:
        print(f"FAIL hard pair uncovered states={uncovered}", file=sys.stderr)
        errors += 1

    if errors == 0:
        print(f"hard_pair ok supports=138 legal_states={legal_states}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["all", "witnesses", "gap-cases", "hard-pair"],
        help="Which exact k=4 computation to run.",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=20,
        help="Largest n used for the explicit witness-family checks.",
    )
    args = parser.parse_args()

    total_errors = 0
    if args.command in {"all", "witnesses"}:
        total_errors += verify_extended_witnesses(args.max_n)
    if args.command in {"all", "gap-cases"}:
        total_errors += verify_gap_cases()
    if args.command in {"all", "hard-pair"}:
        total_errors += verify_hard_pair()
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
