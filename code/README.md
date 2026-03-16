# Reproducibility Code for "A Permutation Avoidance Game with Reverse Replies and Monotone Traps"

This directory contains the clean scripts used to reproduce the computer-assisted
results that are cited in the main paper.

The files are intentionally focused on the main paper only. They do not include
the later exploratory appendix computations.

Toolchain used for the runs cited in the paper:
- C++: `g++` as provided by Apple clang version 17.0.0 (clang-1700.6.4.2)
- Python: Python 3.14.3

## Files

- `pap_starting_data.cpp`
  Reproduces the exact PAP data from the starting position `S_n` that appear in
  Section 2:
  - the SG-values in Table 1,
  - the `k=4` starting-position reverse-strategy test in Proposition 2.7.

- `k4_reverse_reply.py`
  Reproduces the exact `k=4` checks used in Section 6:
  - the table of extended witness families,
  - the residual finite `n=7` verification for the non-hard gap states,
  - the hard-pair computation.

- `bk_thresholds.cpp`
  Reproduces the exact threshold data `N_3=1`, `N_4=7`, `N_5=14`, and `N_6=25`
  from Section 7 by generating the classes `Av_n(B_k)` incrementally until only
  the monotone permutations remain (counted as one permutation at length `1`,
  where increasing and decreasing coincide).

- `k5_fullspace_data.cpp`
  Reproduces the exact `k=5` full-space computations cited in the general-`k`
  discussion and conclusion:
  - the count `28` of non-`B_5`, non-monotone patterns admitting a one-companion
    witness in `S_8`,
  - the count `59` of non-monotone reverse pairs that are separable in `S_8`.

## Typical commands

Compile the C++ tools:

```sh
g++ -O3 -std=c++17 code/pap_starting_data.cpp -o code/pap_starting_data
g++ -O3 -std=c++17 code/bk_thresholds.cpp -o code/bk_thresholds
```

Reproduce the Section 2 starting-position data:

```sh
./code/pap_starting_data table
./code/pap_starting_data reverse-k4
./code/pap_starting_data query 9 4 '1234,4321,1324'
./code/pap_starting_data query 9 4 '1234,4321,1324,4231'
```

Reproduce the Section 6 `k=4` witness computations:

```sh
python3 code/k4_reverse_reply.py all
```

Reproduce the exact threshold computations:

```sh
./code/bk_thresholds 3 6
./code/bk_thresholds 4 10
./code/bk_thresholds 5 20
./code/bk_thresholds 6 30
```

Reproduce the exact `k=5` full-space computations:

```sh
g++ -O3 -std=c++17 code/k5_fullspace_data.cpp -o code/k5_fullspace_data
./code/k5_fullspace_data all
```

The paper's final reproducibility section gives the same commands together with
the corresponding theorem, lemma, and proposition numbers.
