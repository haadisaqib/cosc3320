#!/usr/bin/env python3
"""
hanoi.py - Directed Towers of Hanoi Single-Function Generator (COSC 3320 Style).

Generates a single recursive function F(n, src, aux1, aux2, dst) where parameters
are permuted across recursive calls instead of generating separate mutual functions.
Outputs the complete recurrence and O(3^n) decreasing Master Theorem derivation.
"""

import re
import sys


def parse_v(text):
    tokens = re.findall(r"[A-Za-z_]\w*", text)
    result = []
    for tok in tokens:
        lower_tok = tok.lower()
        if lower_tok != "v" and lower_tok not in result:
            result.append(lower_tok)
    return result


def parse_e(text):
    pairs = re.findall(
        r"\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*\)", text
    )
    edges = []
    for a, b in pairs:
        edges.append((a.lower(), b.lower()))
    return edges


def solve_directed_hanoi_single(v_text, e_text):
    pegs = parse_v(v_text)
    edges = parse_e(e_text)

    # Ensure pegs are populated from edges if V was sparse
    for u, v in edges:
        if u not in pegs:
            pegs.append(u)
        if v not in pegs:
            pegs.append(v)

    # Detect the directed cycle order from Start
    start_peg = "start" if "start" in pegs else pegs[0]
    dest_peg = "dest" if "dest" in pegs else pegs[-1]

    # Build adjacency
    adj = {}
    for p in pegs:
        adj[p] = []
    for u, v in edges:
        if u in adj:
            adj[u].append(v)

    # Trace cycle: Start -> Next1 -> Next2 -> Dest
    cycle = [start_peg]
    curr = start_peg
    for _ in range(len(pegs) - 1):
        neighbors = adj.get(curr, [])
        if not neighbors:
            break
        # Pick neighbor not yet in cycle or completing the cycle
        nxt = None
        for cand in neighbors:
            if cand not in cycle:
                nxt = cand
                break
        if not nxt and neighbors:
            nxt = neighbors[0]
        if nxt:
            cycle.append(nxt)
            curr = nxt

    # Map the detected cycle roles
    # Standard 4-peg cycle: S -> A1 -> A2 -> D -> S
    p_start = cycle[0] if len(cycle) > 0 else "Start"
    p_aux1 = cycle[1] if len(cycle) > 1 else "Aux1"
    p_aux2 = cycle[2] if len(cycle) > 2 else "Aux2"
    p_dest = cycle[3] if len(cycle) > 3 else "Dest"

    separator = "=" * 65
    print(separator)
    print("  COSC 3320 DIRECTED TOWERS OF HANOI (SINGLE-FUNCTION FORM)")
    print(separator)
    print("Graph Specification:")
    print("  V = {" + ", ".join(pegs) + "}")
    print("  E = {" + ", ".join(f"({u}, {v})" for u, v in edges) + "}")
    print(f"  Cycle Order : {p_start} -> {p_aux1} -> {p_aux2} -> {p_dest} -> {p_start}")
    print()

    print(separator)
    print("ALGORITHM (SINGLE RECURSIVE FUNCTION WITH PERMUTED PARAMETERS)")
    print(separator)

    code = f"""def F(n, S, A1, A2, D):
    \"\"\"
    Transfers n disks from peg S to peg D along the directed cycle
    S -> A1 -> A2 -> D -> S using Aux pegs A1 and A2.
    \"\"\"
    if n == 1:
        // Base case: Move disk 1 step-by-step along directed edges to D
        move disk 1 from S to A1;
        move disk 1 from A1 to A2;
        move disk 1 from A2 to D;
    else:
        // 1st recursive call:
        // Park top n-1 disks onto A2 so S is cleared.
        // Directed cycle path S -> A1 -> A2 uses D as the spare intermediate.
        F(n - 1, S, A1, D, A2);

        // Move largest disk n forward 1 step along the directed cycle
        move disk n from S to A1;

        // 2nd recursive call:
        // Relocate n-1 disks from A2 back to S so path ahead is cleared.
        // Directed cycle path A2 -> D -> S uses A1 as the spare intermediate.
        F(n - 1, A2, D, A1, S);

        // Move largest disk n the remaining steps to target D
        move disk n from A1 to A2;
        move disk n from A2 to D;

        // 3rd recursive call:
        // Transfer n-1 disks from S onto D on top of disk n.
        F(n - 1, S, A1, A2, D);

// Initial Call to solve the game:
F(n, {p_start}, {p_aux1}, {p_aux2}, {p_dest});"""

    print(code)
    print()

    print(separator)
    print("TIME COMPLEXITY DERIVATION")
    print(separator)
    print("Recurrence Relation (T = number of moves):")
    print("  Function F makes exactly 3 recursive calls of size n - 1:")
    print("    - Call 1 : F(n - 1, S, A1, D, A2)")
    print("    - Call 2 : F(n - 1, A2, D, A1, S)")
    print("    - Call 3 : F(n - 1, S, A1, A2, D)")
    print("  Plus c = 3 direct moves of disk n (S->A1, A1->A2, A2->D).")
    print()
    print("  T(n) = 3 * T(n - 1) + c")
    print("       = 3 * [3 * T(n - 2) + c] + c = 3^2 * T(n - 2) + (3 + 1)c")
    print("       = ...")
    print("       = 3^(n-1) * T(1) + c * sum_{i=0}^{n-2} 3^i")
    print()
    print("Parameters for Decreasing Master Theorem:")
    print("  Formula : T(n) = r * T(n - d) + c")
    print("  r = 3   (number of recursive calls per function invocation)")
    print("  d = 1   (disk subproblem reduction size: n - 1)")
    print()
    print("Conclusion:")
    print("  By the Decreasing Master Theorem: O(r^(n/d)) = O(3^(n/1)) = O(3^n)")
    print("  Time Complexity: O(3^n)")
    print(separator)


def main():
    if len(sys.argv) >= 3:
        v_in = sys.argv[1]
        e_in = sys.argv[2]
    else:
        v_in = input("v = ").strip()
        e_in = input("e = ").strip()
        if not v_in:
            v_in = "{Start, Aux1, Aux2, Dest}"
        if not e_in:
            e_in = "{(Start, Aux1), (Aux1, Aux2), (Aux2, Dest), (Dest, Start)}"

    solve_directed_hanoi_single(v_in, e_in)


if __name__ == "__main__":
    main()
