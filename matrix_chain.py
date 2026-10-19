#!/usr/bin/env python3
"""
matrix_chain.py - Matrix Chain Multiplication DP Solver (COSC 3320 Exam 1 Style).

Solves:
  M_1 * M_2 * ... * M_n
Supports finding:
  - 'max' (worst-possible parenthesization - Leiss's standard)
  - 'min' (optimal parenthesization)
  - 'avg' (average over all parenthesizations)

Prints the step-by-step formula substitutions, the completed DP table,
the parenthesization string, and the explicit multiplication check.
"""

import re
import sys


def parse_matrices(input_str):
    """
    Parses strings like:
      'M_{9,3} * M_{3,9} * M_{9,1} * M_{1,8} * M_{8,4}'
      or '9x3, 3x9, 9x1, 1x8, 8x4'
      or '9 3 9 1 8 4'
    Returns:
      dimensions list p where matrix i has dimension p[i-1] x p[i]
    """
    pairs = re.findall(r"M_\{?(\d+)\s*,\s*(\d+)\}?", input_str, re.IGNORECASE)
    if pairs:
        dims = [int(pairs[0][0])]
        for _, c in pairs:
            dims.append(int(c))
        return dims

    pairs = re.findall(r"(\d+)\s*[xX,]\s*(\d+)", input_str)
    if pairs:
        dims = [int(pairs[0][0])]
        for _, c in pairs:
            dims.append(int(c))
        return dims

    nums = [int(x) for x in re.findall(r"\d+", input_str)]
    if len(nums) >= 3:
        return nums

    return []


def solve_matrix_chain(dims, mode="max"):
    mode = mode.strip().lower()
    n = len(dims) - 1  # number of matrices

    # S[i][j] stores the DP value for chain M_i ... M_j (1-indexed)
    S = []
    for _ in range(n + 1):
        row = [0] * (n + 1)
        S.append(row)

    # split_k[i][j] stores the best k index
    split_k = []
    for _ in range(n + 1):
        row = [0] * (n + 1)
        split_k.append(row)

    separator = "=" * 70
    print(separator)
    print("  COSC 3320 MATRIX CHAIN MULTIPLICATION DP BREAKDOWN")
    print(separator)
    print("Dimensions vector p:")
    for idx, d in enumerate(dims):
        print(f"  p_{idx} = {d}", end="  ")
    print("\n")

    print(f"Optimization Objective: {mode.upper()}")
    if mode == "max":
        print(
            "Formula: S[i, j] = max_{i <= k < j} { S[i, k] + S[k+1, j] + p_{i-1} * p_k * p_j }"
        )
    elif mode == "min":
        print(
            "Formula: S[i, j] = min_{i <= k < j} { S[i, k] + S[k+1, j] + p_{i-1} * p_k * p_j }"
        )
    else:
        print(
            "Formula: S[i, j] = avg_{i <= k < j} { S[i, k] + S[k+1, j] + p_{i-1} * p_k * p_j }"
        )
    print("Base Cases: S[i, i] = 0 for all i in 1..n\n")

    print("-" * 70)
    print("STEP-BY-STEP DIAGONAL EVALUATIONS")
    print("-" * 70)

    # Fill table diagonally: length L from 2 to n
    for L in range(2, n + 1):
        print(f"\n--- Chains of Length L = {L} ---")
        for i in range(1, n - L + 2):
            j = i + L - 1
            candidates = []

            for k in range(i, j):
                scalar_mult = dims[i - 1] * dims[k] * dims[j]
                cost = S[i][k] + S[k + 1][j] + scalar_mult
                candidates.append((cost, k, S[i][k], S[k + 1][j], scalar_mult))

            if mode == "max":
                chosen_cost, chosen_k, left_s, right_s, mult = max(
                    candidates, key=lambda item: item[0]
                )
            elif mode == "min":
                chosen_cost, chosen_k, left_s, right_s, mult = min(
                    candidates, key=lambda item: item[0]
                )
            else:
                total_cost = 0
                for item in candidates:
                    total_cost = total_cost + item[0]
                chosen_cost = total_cost / len(candidates)
                chosen_k = candidates[0][1]

            S[i][j] = chosen_cost
            split_k[i][j] = chosen_k

            # Print exact work as required by Leiss
            print(f"S[{i}, {j}]:")
            for c, k, left_s, right_s, mult in candidates:
                p_term = f"p_{i-1}*p_{k}*p_{j} = {dims[i-1]}*{dims[k]}*{dims[j]} = {mult}"
                print(
                    f"    k = {k}: S[{i},{k}] + S[{k+1},{j}] + ({p_term}) = {left_s} + {right_s} + {mult} = {c}"
                )
            print(f"  => Chosen S[{i}, {j}] = {chosen_cost} (at k = {chosen_k})")

    # Step 4: Reconstruct Parenthesization
    def get_parens(i, j):
        if i == j:
            return f"M_{dims[i-1]},{dims[i]}"
        k = split_k[i][j]
        left_str = get_parens(i, k)
        right_str = get_parens(k + 1, j)
        return f"({left_str} * {right_str})"

    best_parens = get_parens(1, n)

    # Step 5: Print Completed Upper Triangular Table
    print("\n" + separator)
    print("COMPLETED DYNAMIC PROGRAMMING TABLE S[i, j]")
    print(separator)
    header = "     " + "".join(f"{col:>10}" for col in range(1, n + 1))
    print(header)
    print("     " + "-" * (10 * n))
    for r in range(1, n + 1):
        row_str = f"{r:>3} |"
        for c in range(1, n + 1):
            if c < r:
                row_str += f"{'':>10}"
            else:
                val = S[r][c]
                if isinstance(val, float):
                    row_str += f"{val:>10.1f}"
                else:
                    row_str += f"{val:>10}"
        print(row_str)

    # Step 6: Print Final Answer and Multiplication Check
    print("\n" + separator)
    print("FINAL EXAM DELIVERABLE")
    print(separator)
    final_val = S[1][n]
    print(f"Target Parenthesization:\n  {best_parens}\n")
    print(f"Total Scalar Multiplications Required:\n  S[1, {n}] = {final_val}\n")

    # Explicit check
    print("Multiplication Check Step-by-Step:")
    matrices_stack = []
    # Evaluate check order from parenthesization tree
    check_steps = []

    def eval_check(i, j):
        if i == j:
            return (dims[i - 1], dims[j])
        k = split_k[i][j]
        r1, c1 = eval_check(i, k)
        r2, c2 = eval_check(k + 1, j)
        cost = r1 * c1 * c2
        check_steps.append((f"M_{r1},{c1} * M_{r2},{c2}", f"M_{r1},{c2}", cost))
        return (r1, c2)

    eval_check(1, n)
    running_sum = 0
    for op, res, cost in check_steps:
        running_sum = running_sum + cost
        print(f"  {op:<22} => {res:<12} (Cost: {cost})")
    print(f"  Total Verified Cost = {running_sum}")
    print(separator)


def main():
    if len(sys.argv) >= 2:
        raw_input = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) >= 3 else "max"
    else:
        print("Enter product (e.g., 'M_{9,3} * M_{3,9} * M_{9,1} * M_{1,8} * M_{8,4}')")
        raw_input = input("Product or dimensions: ").strip()
        if not raw_input:
            raw_input = "M_{9,3} * M_{3,9} * M_{9,1} * M_{1,8} * M_{8,4}"

        mode_input = input("Mode (max / min / avg) [max]: ").strip()
        mode = mode_input if mode_input else "max"

    dims = parse_matrices(raw_input)
    if not dims or len(dims) < 3:
        sys.exit(
            "Could not parse matrix dimensions. Example format: M_{9,3} * M_{3,9} * M_{9,1}"
        )

    solve_matrix_chain(dims, mode)


if __name__ == "__main__":
    main()
