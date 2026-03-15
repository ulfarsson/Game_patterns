# permuta-based Python Port for "A Permutation Avoidance Game with Reverse Replies and Monotone Traps"

This directory contains a Python reimplementation of the paper's
computer-assisted checks using the `permuta` library.

These scripts were checked with `Python 3.11` and `permuta`.
Install `permuta` in your Python environment and run the commands below from
the repository root.

Current status by task:
- `k4_reverse_reply_permuta.py`
  Working. Reproduces the Section 6 exact checks:
  extended witnesses, residual `n=7` gap cases, and the hard pair.
- `k5_fullspace_data_permuta.py`
  Working. Reproduces the `k=5` full-space counts from the general-`k`
  discussion and conclusion.
- `bk_thresholds_permuta.py`
  Working for `k <= 5` on this machine. The `k=6` computation is the first
  case that looks too slow for a routine permuta-only replacement.
- `pap_starting_data_permuta.py`
  Working. Reproduces the Section 2 starting-position data:
  Table 1, the `k=4` starting-position reverse-strategy test, exact optimal-play
  length distributions, and exact query states from `S_n`.

Observed timings on this machine:
- `k5_fullspace_data_permuta.py all`: about 1.4 seconds
- `k4_reverse_reply_permuta.py all`: a few seconds
- `bk_thresholds_permuta.py 5 20`: well under a second
- `bk_thresholds_permuta.py 6 12 --max-seconds-per-count 5`: reaches
  `n=11`, but that single `count(11)` call took about 22.8 seconds
- `pap_starting_data_permuta.py reverse-k4`: about 12.4 seconds
- `pap_starting_data_permuta.py sg 9 4`: about 2.5 seconds
- `pap_starting_data_permuta.py table`: about 28.8 seconds

Typical commands:

```sh
python \
  code-permuta/k4_reverse_reply_permuta.py all

python \
  code-permuta/k5_fullspace_data_permuta.py all

python \
  code-permuta/bk_thresholds_permuta.py 5 20

python \
  code-permuta/pap_starting_data_permuta.py table

python \
  code-permuta/pap_starting_data_permuta.py reverse-k4

python \
  code-permuta/pap_starting_data_permuta.py optimal-dist 10 4

python \
  code-permuta/pap_starting_data_permuta.py query 9 4 '1234,4321,1324'
```

Ignoring the deliberately omitted `N_6` threshold computation, this directory
now covers the main paper's proof-critical computations in Python. The main
remaining tradeoff versus `code/` is runtime, especially for the full
starting-position SG table.

Output convention:
- these scripts print permutations in permuta's native zero-based notation,
  for example `2301` for the classical pattern `3412`.
