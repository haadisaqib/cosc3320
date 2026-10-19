#!/usr/bin/env python3
"""
quicksort_builder.py - Comprehensive QuickSort Solver (COSC 3320 Exam 1 Style).
Fixed worst-case adversarial permutations for lo+1 and middle-element pivots.
"""

import sys


def get_pivot_index(sub_len, rule):
    rule = rule.strip().lower()
    if "mid" in rule or "middle" in rule:
        return (sub_len - 1) // 2
    elif "hi" in rule or "last" in rule:
        return sub_len - 1
    elif "lo+1" in rule or "second" in rule or "+1" in rule:
        return 1 if sub_len > 1 else 0
    else:
        return 0


def generate_optimal_array(n, rule):
    elements = list(range(1, n + 1))

    def reverse_build(arr):
        if len(arr) <= 1:
            return arr

        mid_idx = len(arr) // 2
        median_val = arr[mid_idx]

        left_half = [arr[i] for i in range(0, mid_idx)]
        right_half = [arr[i] for i in range(mid_idx + 1, len(arr))]

        rec_left = reverse_build(left_half)
        rec_right = reverse_build(right_half)

        combined = []
        combined.extend(rec_left)
        combined.extend(rec_right)

        p_idx = get_pivot_index(len(arr), rule)
        res = combined[:p_idx] + [median_val] + combined[p_idx:]
        return res

    return reverse_build(elements)


def generate_worst_array(n, rule):
    """
    Constructs an array where the pivot chosen by 'rule'
    is always an extreme value (minimum), maximizing recursion tree depth.
    """
    elements = list(range(1, n + 1))

    def reverse_worst(arr):
        if len(arr) <= 1:
            return arr

        min_val = arr[0]
        rest = arr[1:]
        rec_rest = reverse_worst(rest)

        p_idx = get_pivot_index(len(arr), rule)
        # Place the minimum exactly at the pivot index
        return rec_rest[:p_idx] + [min_val] + rec_rest[p_idx:]

    return reverse_worst(elements)


def simulate_quicksort_trace(arr, rule):
    logs = []

    def qsort(sub, depth):
        if len(sub) <= 1:
            return sub

        p_idx = get_pivot_index(len(sub), rule)
        pivot = sub[p_idx]

        left_side = []
        right_side = []

        for idx in range(len(sub)):
            if idx == p_idx:
                continue
            item = sub[idx]
            if item <= pivot:
                left_side.append(item)
            else:
                right_side.append(item)

        indent = "  " * depth
        logs.append(
            f"{indent}Subarray: {sub}\n"
            f"{indent}  => Pivot = {pivot} | Left ({len(left_side)}): {left_side} | Right ({len(right_side)}): {right_side}"
        )

        sorted_left = qsort(left_side, depth + 1)
        sorted_right = qsort(right_side, depth + 1)
        return sorted_left + [pivot] + sorted_right

    qsort(arr, 0)
    return logs


def run(n, rule):
    rule_clean = rule.strip().lower()
    if "mid" in rule_clean or "middle" in rule_clean:
        rule_desc = "A[floor((lo + hi) / 2)] (middle element)"
    elif "hi" in rule_clean or "last" in rule_clean:
        rule_desc = "A[hi] (last element)"
    elif "lo+1" in rule_clean or "second" in rule_clean or "+1" in rule_clean:
        rule_desc = "A[lo+1] (second element)"
    else:
        rule_desc = "A[lo] (first element)"

    separator = "=" * 70
    print(separator)
    print("  COSC 3320 GENERALIZED QUICKSORT SOLVER & VERIFIER")
    print(separator)
    print("Given Parameters:")
    print(f"  - Array size (n) : {n}")
    print(f"  - Pivot rule     : {rule_desc}")
    print()

    # Part (a): Optimal
    opt_arr = generate_optimal_array(n, rule)
    print("-" * 70)
    print("(a) OPTIMAL EXECUTION (Equal-Sized Splits => O(n log n))")
    print("-" * 70)
    print("Array assignment:")
    print("  " + ", ".join(str(x) for x in opt_arr))
    print()
    print("Explanation to write on exam:")
    print("  QuickSort executes optimally when each chosen pivot is the exact")
    print("  median of the active subarray, splitting the remaining elements into two")
    print(f"  equal-sized subproblems. The array is arranged so that the median")
    print(f"  is positioned at the designated pivot slot ({rule_desc}).")
    print()
    print("Partition Verification Trace:")
    for line in simulate_quicksort_trace(opt_arr, rule)[:6]:
        print(line)
    print("  ... (all recursive subproblems remain balanced)")
    print()

    # Part (b): Slowest
    worst_arr = generate_worst_array(n, rule)
    print("-" * 70)
    print("(b) SLOWEST POSSIBLE EXECUTION (Maximally Unbalanced => O(n^2))")
    print("-" * 70)
    print("Array assignment:")
    print("  " + ", ".join(str(x) for x in worst_arr))
    print()
    print("Explanation to write on exam:")
    print("  The slowest execution occurs when the chosen pivot consistently isolates")
    print("  an extreme value (e.g. minimum), yielding an empty partition (size 0) and")
    print("  a subproblem of size k-1 at each step. This forces recursion depth to n,")
    print("  yielding sum(k) = O(n^2) operations.")
    print()
    print("Partition Verification Trace (First 3 Steps):")
    for line in simulate_quicksort_trace(worst_arr, rule)[:6]:
        print(line)
    print("  ... (degrades linearly down to depth n-1)")
    print(separator)


def main():
    if len(sys.argv) >= 2:
        try:
            n = int(sys.argv[1])
        except ValueError:
            sys.exit("Error: Array size n must be an integer.")
        rule = sys.argv[2] if len(sys.argv) >= 3 else "lo"
    else:
        n_input = input("Enter array size n [15]: ").strip()
        n = int(n_input) if n_input else 15
        rule_input = input("Pivot selection rule (lo, lo+1, hi, mid) [lo]: ").strip()
        rule = rule_input if rule_input else "lo"

    run(n, rule)


if __name__ == "__main__":
    main()