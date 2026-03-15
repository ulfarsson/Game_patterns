#!/usr/bin/env python3
"""README

permuta-assisted Python reimplementation of the starting-position computations
from Section 2 of the paper.

What it computes:
- the exact SG-values in Table 1 for 1 <= k <= 4;
- the exact starting-position reverse-strategy test for k = 4;
- exact optimal-play length distributions from the starting position S_n;
- exact query states from the starting position S_n.

Design notes:
- permuta is used for pattern parsing and symmetry operations;
- the game solver itself is a direct Python port of the profile-reduction method
  from code/pap_starting_data.cpp, since that part is not already available in
  permuta.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import combinations, islice, permutations
from math import factorial
from time import perf_counter

from permuta import Perm


class SolveResult:
    __slots__ = ("sg", "sg_table", "subset_or", "profiles", "multiplicities")

    def __init__(self, sg, sg_table, subset_or, profiles, multiplicities):
        self.sg = sg
        self.sg_table = sg_table
        self.subset_or = subset_or
        self.profiles = profiles
        self.multiplicities = multiplicities


@lru_cache(None)
def pattern_list(k: int) -> tuple[Perm, ...]:
    return tuple(Perm(p) for p in permutations(range(k)))


@lru_cache(None)
def pattern_rank_map(k: int) -> dict[Perm, int]:
    return {perm: idx for idx, perm in enumerate(pattern_list(k))}


@lru_cache(None)
def combinations_of(n: int, k: int) -> tuple[tuple[int, ...], ...]:
    return tuple(combinations(range(n), k))


def parse_patterns(text: str) -> tuple[Perm, ...]:
    if text in {"", "-"}:
        return tuple()
    return tuple(sorted(Perm.to_standard(token.strip()) for token in text.split(",") if token.strip()))


def standardized_rank_generic(values, rank_map) -> int:
    return rank_map[Perm.to_standard(values)]


def standardized_rank4(a: int, b: int, c: int, d: int) -> int:
    return ((b < a) + (c < a) + (d < a)) * 6 + ((c < b) + (d < b)) * 2 + (d < c)


def standardized_rank3(a: int, b: int, c: int) -> int:
    return ((b < a) + (c < a)) * 2 + (c < b)


def collect_profile_counts(n: int, k: int) -> dict[int, int]:
    if not (1 <= k <= 4):
        raise ValueError("This script supports only 1 <= k <= 4.")
    if k > n:
        return {0: 1}

    combos = combinations_of(n, k)
    counts: dict[int, int] = {}

    if k == 1:
        return {1: factorial(n)}

    if k == 2:
        for perm in permutations(range(n)):
            mask = 0
            for i0, i1 in combos:
                mask |= 1 << (perm[i1] < perm[i0])
            counts[mask] = counts.get(mask, 0) + 1
        return counts

    if k == 3:
        for perm in permutations(range(n)):
            mask = 0
            for i0, i1, i2 in combos:
                mask |= 1 << standardized_rank3(perm[i0], perm[i1], perm[i2])
            counts[mask] = counts.get(mask, 0) + 1
        return counts

    if k == 4:
        for perm in permutations(range(n)):
            mask = 0
            for i0, i1, i2, i3 in combos:
                mask |= 1 << standardized_rank4(perm[i0], perm[i1], perm[i2], perm[i3])
            counts[mask] = counts.get(mask, 0) + 1
        return counts

    rank_map = pattern_rank_map(k)
    for perm in permutations(range(n)):
        mask = 0
        for idxs in combos:
            mask |= 1 << standardized_rank_generic(tuple(perm[i] for i in idxs), rank_map)
        counts[mask] = counts.get(mask, 0) + 1
    return counts


def solve_from_profile_counts(profile_counts: dict[int, int], pattern_count: int) -> SolveResult:
    full_mask = (1 << pattern_count) - 1
    state_count = 1 << pattern_count

    subset_or = [0] * state_count
    profiles = sorted(profile_counts)
    multiplicities = [profile_counts[p] for p in profiles]
    for profile in profiles:
        subset_or[profile] |= profile

    for bit in range(pattern_count):
        half = 1 << bit
        step = half << 1
        for base in range(0, state_count, step):
            upper = base + half
            for idx in range(half):
                subset_or[upper + idx] |= subset_or[base + idx]

    sg_table = [0] * state_count
    for state in range(full_mask, -1, -1):
        legal = subset_or[full_mask ^ state]
        seen = 0
        while legal:
            move_bit = legal & -legal
            legal ^= move_bit
            seen |= 1 << sg_table[state | move_bit]
        mex = 0
        while (seen >> mex) & 1:
            mex += 1
        sg_table[state] = mex

    return SolveResult(sg_table[0], sg_table, subset_or, profiles, multiplicities)


@lru_cache(None)
def solve_starting_position(n: int, k: int) -> SolveResult:
    if not (1 <= k <= 4):
        raise ValueError("This script supports only 1 <= k <= 4.")
    if k > n:
        return SolveResult(0, [0], [0], [0], [1])
    profile_counts = collect_profile_counts(n, k)
    return solve_from_profile_counts(profile_counts, factorial(k))


@lru_cache(None)
def reverse_image(k: int) -> tuple[int, ...]:
    ranks = pattern_rank_map(k)
    return tuple(ranks[perm.reverse()] for perm in pattern_list(k))


def forced_reverse_holds_rec(state: int, full_mask: int, result: SolveResult, rev_image, memo) -> bool:
    known = memo.get(state)
    if known is not None:
        return known

    legal = result.subset_or[full_mask ^ state]
    while legal:
        move_bit = legal & -legal
        legal ^= move_bit
        move = move_bit.bit_length() - 1
        after_move = state | move_bit
        reply_bit = 1 << rev_image[move]

        if after_move & reply_bit:
            memo[state] = False
            return False
        if (result.subset_or[full_mask ^ after_move] & reply_bit) == 0:
            memo[state] = False
            return False

        after_reply = after_move | reply_bit
        if result.sg_table[after_reply] != 0:
            memo[state] = False
            return False
        if not forced_reverse_holds_rec(after_reply, full_mask, result, rev_image, memo):
            memo[state] = False
            return False

    memo[state] = True
    return True


def forced_reverse_holds(n: int, k: int) -> bool:
    if k > n:
        return True
    result = solve_starting_position(n, k)
    full_mask = (1 << factorial(k)) - 1
    return forced_reverse_holds_rec(0, full_mask, result, reverse_image(k), {})


def forbidden_mask(patterns: tuple[Perm, ...], k: int) -> int:
    ranks = pattern_rank_map(k)
    mask = 0
    for pattern in patterns:
        mask |= 1 << ranks[pattern]
    return mask


def survivor_count(state: int, result: SolveResult) -> int:
    total = 0
    for profile, multiplicity in zip(result.profiles, result.multiplicities):
        if (profile & state) == 0:
            total += multiplicity
    return total


def winning_moves(state: int, k: int, result: SolveResult) -> list[Perm]:
    full_mask = (1 << factorial(k)) - 1
    out = []
    legal = result.subset_or[full_mask ^ state]
    patterns = pattern_list(k)
    while legal:
        move_bit = legal & -legal
        legal ^= move_bit
        if result.sg_table[state | move_bit] == 0:
            out.append(patterns[move_bit.bit_length() - 1])
    return out


def _shift_distribution(child: tuple[int, ...], out: list[int]) -> None:
    for length, count in enumerate(child):
        if count:
            out[length + 1] += count


def complete_play_distribution(n: int, k: int, optimal_only: bool) -> dict[int, int]:
    if not (1 <= k <= 4):
        raise ValueError("This script supports only 1 <= k <= 4.")

    result = solve_starting_position(n, k)
    pattern_count = factorial(k)
    full_mask = (1 << pattern_count) - 1
    max_length = pattern_count

    @lru_cache(None)
    def distribution(state: int) -> tuple[int, ...]:
        legal = result.subset_or[full_mask ^ state]
        if not legal:
            out = [0] * (max_length + 1)
            out[0] = 1
            return tuple(out)

        out = [0] * (max_length + 1)
        while legal:
            move_bit = legal & -legal
            legal ^= move_bit
            next_state = state | move_bit
            if optimal_only and result.sg_table[state] != 0 and result.sg_table[next_state] != 0:
                continue
            _shift_distribution(distribution(next_state), out)
        return tuple(out)

    return {length: count for length, count in enumerate(distribution(0)) if count}


def benchmark_profiles(n: int, k: int, sample: int) -> None:
    idxs = combinations_of(n, k)
    perms = list(islice(permutations(range(n)), sample))
    t0 = perf_counter()
    for perm in perms:
        _ = {Perm.to_standard(tuple(perm[i] for i in idx)) for idx in idxs}
    t1 = perf_counter()
    per_perm = (t1 - t0) / sample
    print(f"sample={sample} n={n} k={k} secs={t1 - t0:.3f}")
    print(f"per_perm_ms={1000.0 * per_perm:.4f}")
    print(f"projected_full_secs={per_perm * factorial(n):.1f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("table", help="Print the exact SG table from Section 2.")
    sub.add_parser("reverse-k4", help="Test the exact starting-position reverse reply for k=4.")

    sg_cmd = sub.add_parser("sg", help="Compute the exact SG value of the starting position S_n.")
    sg_cmd.add_argument("n", type=int)
    sg_cmd.add_argument("k", type=int)

    reverse_cmd = sub.add_parser("reverse", help="Test whether forced reversal wins from S_n.")
    reverse_cmd.add_argument("n", type=int)
    reverse_cmd.add_argument("k", type=int)

    optimal_dist = sub.add_parser(
        "optimal-dist",
        help="Exact distribution of complete play lengths under optimal play from S_n.",
    )
    optimal_dist.add_argument("n", type=int)
    optimal_dist.add_argument("k", type=int)

    all_dist = sub.add_parser(
        "all-dist",
        help="Exact distribution of complete play lengths over all complete plays from S_n.",
    )
    all_dist.add_argument("n", type=int)
    all_dist.add_argument("k", type=int)

    query = sub.add_parser("query", help="Exact query state from the starting position S_n.")
    query.add_argument("n", type=int)
    query.add_argument("k", type=int)
    query.add_argument("patterns", help="Comma-separated forbidden patterns, e.g. 1234,4321,1324")

    bench = sub.add_parser("benchmark-profiles", help="Estimate profile-collection cost.")
    bench.add_argument("n", type=int)
    bench.add_argument("k", type=int)
    bench.add_argument("--sample", type=int, default=2000)

    args = parser.parse_args()

    if args.command == "table":
        for n in range(1, 11):
            for k in range(1, 5):
                result = solve_starting_position(n, k)
                print(f"n={n} k={k} sg={result.sg}")
        return 0

    if args.command == "reverse-k4":
        for n in range(4, 10):
            print(f"n={n} forced_reverse={'yes' if forced_reverse_holds(n, 4) else 'no'}")
        return 0

    if args.command == "sg":
        result = solve_starting_position(args.n, args.k)
        print(f"n={args.n} k={args.k} sg={result.sg}")
        return 0

    if args.command == "reverse":
        print(f"n={args.n} k={args.k} forced_reverse={'yes' if forced_reverse_holds(args.n, args.k) else 'no'}")
        return 0

    if args.command == "query":
        result = solve_starting_position(args.n, args.k)
        state = forbidden_mask(parse_patterns(args.patterns), args.k)
        print(f"n={args.n} k={args.k} sg={result.sg_table[state]} survivors={survivor_count(state, result)}")
        print("winning_moves=" + ",".join(str(p) for p in winning_moves(state, args.k, result)))
        return 0

    if args.command == "optimal-dist":
        distribution = complete_play_distribution(args.n, args.k, optimal_only=True)
        print(f"n={args.n} k={args.k} optimal_play_distribution")
        for length, count in distribution.items():
            print(f"{length} {count}")
        return 0

    if args.command == "all-dist":
        distribution = complete_play_distribution(args.n, args.k, optimal_only=False)
        print(f"n={args.n} k={args.k} all_play_distribution")
        for length, count in distribution.items():
            print(f"{length} {count}")
        return 0

    benchmark_profiles(args.n, args.k, args.sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
