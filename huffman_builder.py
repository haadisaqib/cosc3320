#!/usr/bin/env python3
"""
huffman_builder.py - Visual Optimal Huffman Code Builder (COSC 3320).

Prints:
  1. Forest merging trace with intermediate subtree representations.
  2. Complete final 2D ASCII binary tree with labeled 0/1 branch paths.
  3. Formatted code table and expected length bit size calculation.
"""

import heapq
import re
import sys


class HNode:
    def __init__(self, weight, symbol=None, left=None, right=None, tie=0):
        self.weight = weight
        self.symbol = symbol
        self.left = left
        self.right = right
        self.tie = tie

    def __lt__(self, other):
        if self.weight != other.weight:
            return self.weight < other.weight
        return self.tie < other.tie


def parse_symbols(text):
    tokens = re.findall(r"([A-Za-z0-9_]+)\s*[:=]?\s*(\d+)(?:/(\d+))?", text)
    if not tokens:
        return [], 1
    denom = int(tokens[0][2]) if tokens[0][2] else 1
    items = [(sym, int(num)) for sym, num, _ in tokens]
    return items, denom


def render_ascii_tree(node):
    """
    Renders any Huffman binary node into formatted ASCII text rows.
    """
    if node is None:
        return [], 0, 0, 0

    if node.symbol is not None:
        val_str = f"[{node.symbol}:{node.weight}]"
    else:
        val_str = f"({node.weight})"

    left_lines, left_pos, left_width, _ = render_ascii_tree(node.left)
    right_lines, right_pos, right_width, _ = render_ascii_tree(node.right)
    val_len = len(val_str)

    if not left_lines and not right_lines:
        return [val_str], val_len // 2, val_len, 1

    if left_lines and not right_lines:
        first_line = " " * (left_pos + 1) + "_0_" * ((left_width - left_pos - 1) // 3 + 1) + val_str
        second_line = " " * left_pos + "/" + " " * (len(first_line) - left_pos - 1)
        shifted = [l + " " * val_len for l in left_lines]
        return [first_line, second_line] + shifted, len(first_line) - val_len // 2, len(first_line), len(shifted) + 2

    if right_lines and not left_lines:
        first_line = val_str + "_1_" * (right_pos // 3 + 1) + " " * (right_width - right_pos)
        second_line = " " * (val_len + right_pos) + "\\" + " " * (right_width - right_pos - 1)
        shifted = [" " * val_len + l for l in right_lines]
        return [first_line, second_line] + shifted, val_len // 2, len(first_line), len(shifted) + 2

    # Both children present
    gap = 2
    left_arm = max(1, left_width - left_pos - 1)
    right_arm = max(1, right_pos)

    first_line = (
        " " * (left_pos + 1)
        + "-" * left_arm
        + "(0)"
        + val_str
        + "(1)"
        + "-" * right_arm
        + " " * (right_width - right_pos)
    )
    second_line = (
        " " * left_pos
        + "/"
        + " " * (len(first_line) - left_pos - right_width + right_pos - 1)
        + "\\"
        + " " * (right_width - right_pos - 1)
    )

    shifted = []
    max_h = max(len(left_lines), len(right_lines))
    for i in range(max_h):
        l_part = left_lines[i] if i < len(left_lines) else " " * left_width
        r_part = right_lines[i] if i < len(right_lines) else " " * right_width
        shifted.append(l_part + " " * (len(first_line) - left_width - right_width) + r_part)

    root_pos = left_pos + 1 + left_arm + 3 + val_len // 2
    return [first_line, second_line] + shifted, root_pos, len(first_line), len(shifted) + 2


def run_visual_huffman(text):
    items, denom = parse_symbols(text)
    if not items:
        sys.exit("Error: Could not parse symbols.")

    sep = "=" * 70
    print(sep)
    print("  COSC 3320 VISUAL HUFFMAN CODE & TREE GENERATOR")
    print(sep)
    print("Symbols and Frequencies:")
    for s, w in items:
        p_str = f"{w}/{denom}" if denom > 1 else str(w)
        print(f"  {s}: {p_str}", end="   ")
    print("\n")

    heap = []
    counter = 0
    for s, w in items:
        counter += 1
        heapq.heappush(heap, HNode(w, symbol=s, tie=counter))

    print("-" * 70)
    print("FOREST MERGE SEQUENCE (Step-by-Step Tree Combination)")
    print("-" * 70)
    step = 1
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        parent_wt = n1.weight + n2.weight
        counter += 1
        # n1 is assigned '0' (left), n2 is assigned '1' (right)
        parent = HNode(parent_wt, left=n1, right=n2, tie=counter)

        s1 = f"[{n1.symbol}:{n1.weight}]" if n1.symbol else f"(subweight {n1.weight})"
        s2 = f"[{n2.symbol}:{n2.weight}]" if n2.symbol else f"(subweight {n2.weight})"
        print(f"Merge #{step}: Combine {s1} (left=0) + {s2} (right=1) -> New Node ({parent_wt})")
        heapq.heappush(heap, parent)
        step += 1

    root = heap[0]

    # Assign bit codes
    codes = {}

    def get_codes(node, curr_code):
        if node.symbol is not None:
            codes[node.symbol] = curr_code if curr_code else "0"
            return
        if node.left:
            get_codes(node.left, curr_code + "0")
        if node.right:
            get_codes(node.right, curr_code + "1")

    get_codes(root, "")

    # Draw the final tree
    print("\n" + sep)
    print("COMPLETED HUFFMAN BINARY TREE (Draw This in Exam Booklet)")
    print("Branches: Left = 0, Right = 1")
    print(sep)
    tree_lines, _, _, _ = render_ascii_tree(root)
    for line in tree_lines:
        print("  " + line)
    print()

    # Output code table
    print(sep)
    print("ASSIGNED CODES AND EXPECTED LENGTH")
    print(sep)
    print(f"{'Symbol':<10} | {'Probability':<15} | {'Bit Code':<15} | {'Length':<10}")
    print("-" * 70)
    total_bits = 0
    for s, w in items:
        code = codes[s]
        l = len(code)
        p_str = f"{w}/{denom}" if denom > 1 else str(w)
        print(f"{s:<10} | {p_str:<15} | {code:<15} | {l:<10}")
        total_bits += w * l

    expected_len = total_bits / denom
    print("-" * 70)
    print(f"Expected Bit Length = sum(Prob * Length) = ({total_bits}) / {denom} = {expected_len:.4f} bits")
    print(sep)


def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter symbol frequencies [e.g. a 1/40 b 2/40 c 3/40 d 4/40 e 5/40 f 6/40 g 6/40 h 13/40]: ").strip()
        if not text:
            text = "a 1/40 b 2/40 c 3/40 d 4/40 e 5/40 f 6/40 g 6/40 h 13/40"
    run_visual_huffman(text)


if __name__ == "__main__":
    main()
