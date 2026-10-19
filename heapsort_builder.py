#!/usr/bin/env python3
"""
heapsort_builder.py - Visual HeapSort Solver for Exam Paper Copying (COSC 3320).

Prints:
  1. 1D Array state after each insertion / extraction.
  2. Full 2D ASCII binary tree diagrams after each step.
"""

import sys


def print_heap_tree(heap, label=""):
    """
    Renders a 1D heap array as a formatted ASCII binary tree.
    """
    if not heap:
        print("  (Empty Heap)")
        return

    n = len(heap)
    lines = []

    def build_tree_lines(idx):
        if idx >= n:
            return [], 0, 0, 0

        val_str = f"({heap[idx]})"
        left_idx = 2 * idx + 1
        right_idx = 2 * idx + 2

        left_lines, left_pos, left_width, _ = build_tree_lines(left_idx)
        right_lines, right_pos, right_width, _ = build_tree_lines(right_idx)

        val_len = len(val_str)

        if not left_lines and not right_lines:
            return [val_str], val_len // 2, val_len, 1

        if left_lines and not right_lines:
            first_line = " " * (left_pos + 1) + "_" * (left_width - left_pos - 1) + val_str
            second_line = " " * left_pos + "/" + " " * (left_width - left_pos - 1 + val_len)
            shifted_lines = [l + " " * val_len for l in left_lines]
            return [first_line, second_line] + shifted_lines, left_width + val_len // 2, left_width + val_len, len(shifted_lines) + 2

        if right_lines and not left_lines:
            first_line = val_str + "_" * right_pos + " " * (right_width - right_pos)
            second_line = " " * (val_len + right_pos) + "\\" + " " * (right_width - right_pos - 1)
            shifted_lines = [" " * val_len + l for l in right_lines]
            return [first_line, second_line] + shifted_lines, val_len // 2, val_len + right_width, len(shifted_lines) + 2

        # Both children present
        left_branch_len = left_width - left_pos - 1
        right_branch_len = right_pos

        first_line = (
            " " * (left_pos + 1)
            + "_" * left_branch_len
            + val_str
            + "_" * right_branch_len
            + " " * (right_width - right_pos)
        )
        second_line = (
            " " * left_pos
            + "/"
            + " " * (left_branch_len + val_len + right_branch_len)
            + "\\"
            + " " * (right_width - right_pos - 1)
        )

        pad = 2
        shifted_lines = []
        max_h = max(len(left_lines), len(right_lines))
        for i in range(max_h):
            l_part = left_lines[i] if i < len(left_lines) else " " * left_width
            r_part = right_lines[i] if i < len(right_lines) else " " * right_width
            shifted_lines.append(l_part + " " * (val_len + pad) + r_part)

        root_pos = left_width + pad // 2 + val_len // 2
        total_w = left_width + val_len + pad + right_width
        return [first_line, second_line] + shifted_lines, root_pos, total_w, len(shifted_lines) + 2

    tree_rows, _, _, _ = build_tree_lines(0)
    if label:
        print(f"  {label}")
    for row in tree_rows:
        print("    " + row)
    print()


def sift_up(heap, idx):
    while idx > 0:
        parent = (idx - 1) // 2
        if heap[idx] > heap[parent]:
            heap[idx], heap[parent] = heap[parent], heap[idx]
            idx = parent
        else:
            break


def sift_down(heap, length, idx):
    while True:
        largest = idx
        left = 2 * idx + 1
        right = 2 * idx + 2

        if left < length and heap[left] > heap[largest]:
            largest = left
        if right < length and heap[right] > heap[largest]:
            largest = right

        if largest != idx:
            heap[idx], heap[largest] = heap[largest], heap[idx]
            idx = largest
        else:
            break


def run_visual_heapsort(elements):
    sep = "=" * 70
    print(sep)
    print("  COSC 3320 VISUAL HEAPSORT (TREE & ARRAY FOR EXAM BOOKLET)")
    print(sep)
    print("Initial Input Array:", elements)
    print()

    # Part (a): Max-Heap Construction
    print("-" * 70)
    print("(a) MAX-HEAP INSERTIONS (Step-by-Step Tree Building)")
    print("-" * 70)
    heap = []
    for step, val in enumerate(elements, start=1):
        heap.append(val)
        sift_up(heap, len(heap) - 1)
        print(f"--- Step {step}: Insert [{val}] ---")
        print(f"Array: {heap}")
        print_heap_tree(heap, label=f"Tree after inserting {val}:")

    # Part (b): Max-Heap Extractions
    print("-" * 70)
    print("(b) MAX-HEAP EXTRACTIONS (Sorting Phase)")
    print("-" * 70)
    sorted_heap = list(heap)
    n = len(sorted_heap)

    for step in range(1, n + 1):
        extracted = sorted_heap[0]
        active_len = n - step + 1

        sorted_heap[0], sorted_heap[active_len - 1] = sorted_heap[active_len - 1], sorted_heap[0]
        sift_down(sorted_heap, active_len - 1, 0)

        active_part = sorted_heap[: active_len - 1]
        sorted_part = sorted_heap[active_len - 1 :]

        print(f"--- Step {step}: Extract Max [{extracted}] ---")
        print(f"Active Heap Array : {active_part}")
        print(f"Sorted Partition  : {sorted_part}")
        if active_part:
            print_heap_tree(active_part, label=f"Active Tree after removing {extracted} & adjusting:")
        else:
            print("  Tree is now empty. Sorting complete!\n")

    print(sep)
    print("FINAL SORTED RESULT:")
    print(" ", sorted_heap)
    print(sep)


def main():
    if len(sys.argv) > 1:
        raw = " ".join(sys.argv[1:])
    else:
        raw = input("Enter numbers to heapify [e.g. 8 1 2 3 5 6 4 7 10 9]: ").strip()
        if not raw:
            raw = "8 1 2 3 5 6 4 7 10 9"

    nums = [int(x) for x in raw.replace(",", " ").split()]
    run_visual_heapsort(nums)


if __name__ == "__main__":
    main()
