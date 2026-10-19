# Results: 3 of 4 scripts broken

## 1. `Hanoi.py` — **BROKEN** (1 crash)
| # | Case | Result |
|---|---|---|
| 1 | 4-peg cycle (baseline) | ✅ |
| 2 | Classic 3-peg | ✅ |
| 3 | 2 pegs, 1 edge | ✅ (correct "impossible") |
| 4 | Disconnected graph | ✅ |
| 5 | 5 pegs | ✅ (drawing degrades gracefully) |
| 6 | Unreachable dest | ✅ |
| 7 | **Pegs named `{S,A1,A2,D}`** | ❌ **EOFError crash** (`Hanoi.py:367`) |
| 8 | Extra/dense edges | ✅ |
| 9 | 2-cycle | ✅ |
| 10 | Empty `V` | ✅ (edges repair it) |

**Bug:** If `V` has no peg literally named `start`/`dest`, it falls back to `input()` — crashing under non-interactive CLI use.
**Fix:** Add optional 3rd/4th CLI args for start/dest, e.g. `start = sys.argv[3] if len(sys.argv) > 3 else ("start" if "start" in pegs else input(...))`, and validate they're in `pegs`.

## 2. `vm_pages.py` — **BROKEN** (3 bugs)
| # | Case | Result |
|---|---|---|
| 1 | 2048/1024/1024 row row | ✅ (matches howto: 8,392,704) |
| 2 | **N=1000 < P** | ❌ claims **0 reads** for sequential B (`N//P = 0`) |
| 3 | **N=10, P=100** | ❌ same — 0 pages |
| 4 | **M=100000 ≥ N** | ❌ still prints "Since M < N, LRU thrashes completely" — `M` is **never used** in logic |
| 5–6 | col layouts | ✅ |
| 7 | **P=0** | ❌ **ZeroDivisionError** (`vm_pages.py:22`) |
| 8–10 | extra args, N=1, mixed | ✅/minor |

**Fixes:** use `ceil(N/P)` (`-(-n // p)`) not `//`; validate `P > 0` and `N ≥ 1`; actually branch on `mem_pages`: strided access thrashes only if `M < N` — otherwise pages stay resident and per-loop transfers drop dramatically (add a `fits = mem_pages >= n` path).

## 3. `quicksort_builder.py` — **BROKEN** (2 wrong outputs + 1 crash)
| # | Case | Result |
|---|---|---|
| 1–4 | n=15 lo / lo+1 / hi / mid optimal arrays | ✅ verified balanced (depth 3) |
| 5–8 | n=1, 2, 0, 16 | ✅ no crash |
| 9 | n=-5 | ⚠️ silent nonsense |
| 10 | n="abc" | ❌ `int()` ValueError crash |
| — | **worst case `lo`** | ✅ depth 14 (max) |
| — | **worst case `hi`** | ✅ |
| — | **worst case `lo+1`** | ❌ sorted array → depth 7 (not maximally unbalanced; second element ≠ extreme) |
| — | **worst case `mid`** | ❌ output has **zeros & duplicates** (not a permutation of 1..n), depth 11 |

**Fixes:**
- `generate_worst_array` for `lo+1`: build recursively so the *second* slot always holds the subarray's minimum (e.g. `[big, min, ...rest]`), giving depth n−1.
- For `mid`: the binary-search fill only populates O(log n) slots, leaving 0s. Instead do the reverse of `reverse_build`: recursively place the subarray minimum at the mid index (move it to `get_pivot_index` slot), fill the rest arbitrarily with larger values.
- Validate `n` is a positive integer; validate `rule` against a whitelist.

## 4. `matrix_chain.py` — **minor issues only**
| # | Case | Result |
|---|---|---|
| 1, 4, 5, 6, 9 | baseline/max/min/labels/x-format | ✅ (1251 verified, matches howto) |
| 3 | **avg mode** | ⚠️ `S[1,5] = 547.5` but "Total Verified Cost = 284" — the check reuses `split_k` (arbitrarily first k), so the verification contradicts the DP value |
| 8 | **invalid chain** `2 3 4 5` (3≠4) | ⚠️ silently computes meaningless numbers |
| 10 | mode `banana` | ⚠️ silently falls into avg branch |
| 7 | single matrix | ✅ clean exit |

**Fixes:** in avg mode either print the split-consistent parenthesization cost or drop the "verified" check; validate `dims[i] == dims[i+1]` chain compatibility (i.e., `p[k]` matches) and warn; validate mode ∈ {max,min,avg}.

**Bottom line:** `matrix_chain.py` is exam-safe for the howto's inputs; `Hanoi.py`, `vm_pages.py`, and `quicksort_builder.py` will give wrong answers or crash on plausible variants (custom peg names; N not a multiple of P or M ≥ N; `lo+1`/`mid` worst-case questions).