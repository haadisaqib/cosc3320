#!/usr/bin/env python3
"""
vm_pages.py - Virtual Memory LRU Page Transfer Calculator (COSC 3320 Exam 1 Style).

Calculates page transfers for:
    for I := 1 to N do
        for J := 1 to N do
            A[J, I] := A[J, I] * B[I, J]

Supports all memory layouts (Row-Major and Column-Major).
"""

import sys


def solve_page_transfers(n, page_size, mem_pages, a_order, b_order):
    # Normalize order strings
    a_order = a_order.strip().lower()
    b_order = b_order.strip().lower()

    # Step 1: Pages per full row/column
    pages_per_vector = n // page_size

    # Step 2: Determine access patterns
    # Matrix A is indexed as A[J, I].
    # In the inner loop, J varies rapidly (1 to N), while I is fixed.
    # - If A is stored Row-Major: incrementing J changes the ROW each iteration (strided / column access).
    # - If A is stored Column-Major: incrementing J moves sequentially down memory (contiguous access).
    if "row" in a_order:
        a_access_type = "strided"
        # Each J step accesses a completely different row.
        # Across N steps, it touches N different pages.
        # Since active memory (mem_pages) < N pages, LRU thrashes on every step.
        a_reads_per_outer_loop = n
        a_writes_per_outer_loop = n
    else:
        a_access_type = "sequential"
        # Accessing Column I sequentially down contiguous memory.
        # Total pages occupied by one column = N / page_size.
        a_reads_per_outer_loop = pages_per_vector
        a_writes_per_outer_loop = pages_per_vector

    # Matrix B is indexed as B[I, J].
    # In the inner loop, J varies rapidly (1 to N), while I is fixed.
    # - If B is stored Row-Major: incrementing J moves sequentially across row I (contiguous access).
    # - If B is stored Column-Major: incrementing J changes the ROW each iteration (strided / column access).
    if "row" in b_order:
        b_access_type = "sequential"
        # Accessing Row I sequentially across contiguous memory.
        # Total pages occupied by one row = N / page_size.
        b_reads_per_outer_loop = pages_per_vector
    else:
        b_access_type = "strided"
        # Strided access down the column. LRU thrashes across N pages.
        b_reads_per_outer_loop = n

    transfers_per_outer_loop = (
        b_reads_per_outer_loop + a_reads_per_outer_loop + a_writes_per_outer_loop
    )
    total_transfers = transfers_per_outer_loop * n

    # Step 3: Print exam-ready derivation
    separator = "=" * 65
    print(separator)
    print("  COSC 3320 VIRTUAL MEMORY PAGE TRANSFER BREAKDOWN")
    print(separator)
    print("Given Parameters:")
    print("  - Array Dimension (N)       :", n)
    print("  - Page Size (P)             :", page_size, "words")
    print("  - Active Memory Limit (M)   :", mem_pages, "pages")
    print("  - Storage Order for Array A :", a_order.capitalize())
    print("  - Storage Order for Array B :", b_order.capitalize())
    print()

    print("Access Analysis per Outer Loop Iteration (I = 1 to N):")
    print("  1. Matrix B[I, J] (Read Only):")
    if b_access_type == "sequential":
        print("     - Pattern : Sequential access across row I.")
        print(
            "     - Pages   : Touches N / P =",
            pages_per_vector,
            "pages per outer loop.",
        )
    else:
        print("     - Pattern : Strided access down column J.")
        print(
            "     - Pages   : Touches N =",
            n,
            "different pages. Since M < N, LRU thrashes completely.",
        )
    print("     - Transfers for B :", b_reads_per_outer_loop, "reads.")
    print()

    print("  2. Matrix A[J, I] (Read & Written Back):")
    if a_access_type == "strided":
        print("     - Pattern : Strided access across rows as J changes.")
        print(
            "     - Pages   : Touches N =",
            n,
            "different pages. Since M < N, LRU thrashes completely.",
        )
        print("     - Each step requires 1 read and 1 write-back to disk.")
    else:
        print("     - Pattern : Sequential access down column I.")
        print(
            "     - Pages   : Touches N / P =",
            pages_per_vector,
            "pages per outer loop.",
        )
        print("     - Total transfers = reads + write-backs.")
    print("     - Transfers for A :", a_reads_per_outer_loop, "reads +", a_writes_per_outer_loop, "writes.")
    print()

    print("Sum per Outer Loop Iteration:")
    print(
        "  Transfers per I-step = (B_reads + A_reads + A_writes) =",
        f"({b_reads_per_outer_loop} + {a_reads_per_outer_loop} + {a_writes_per_outer_loop}) =",
        transfers_per_outer_loop,
        "transfers",
    )
    print()

    print(separator)
    print("FINAL EXAM CALCULATION")
    print(separator)
    print(
        f"  Total Transfers = N * ({b_reads_per_outer_loop} + {a_reads_per_outer_loop} + {a_writes_per_outer_loop})"
    )
    print(f"                  = {n} * {transfers_per_outer_loop}")
    print(f"                  = {total_transfers:,} page transfers")
    print(separator)


def main():
    if len(sys.argv) >= 6:
        n = int(sys.argv[1])
        page_size = int(sys.argv[2])
        mem_pages = int(sys.argv[3])
        a_order = sys.argv[4]
        b_order = sys.argv[5]
    else:
        print("Enter exam parameters (press Enter to accept defaults in brackets):")
        n_input = input("Array dimension N [2048]: ").strip()
        n = int(n_input) if n_input else 2048

        p_input = input("Words per page P [1024]: ").strip()
        page_size = int(p_input) if p_input else 1024

        m_input = input("Active memory limit M [1024]: ").strip()
        mem_pages = int(m_input) if m_input else 1024

        a_input = input("Array A layout (row/col) [row]: ").strip()
        a_order = a_input if a_input else "row"

        b_input = input("Array B layout (row/col) [row]: ").strip()
        b_order = b_input if b_input else "row"

    solve_page_transfers(n, page_size, mem_pages, a_order, b_order)


if __name__ == "__main__":
    main()
