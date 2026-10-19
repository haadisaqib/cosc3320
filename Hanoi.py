#!/usr/bin/env python3
"""
hanoi.py - Towers of Hanoi on a directed peg graph (COSC 3320 exam style).

Type V and E in lower case (any case works):
  v = {start, dest, aux1, aux2}
  e = {(start, dest), (dest, aux1), (aux1, aux2), (aux2, start)}

Prints: the graph drawing, the algorithm (pseudocode), and the time complexity.

Run:  python3 hanoi.py
  or: python3 hanoi.py "{start, dest, aux1, aux2}" "{(start,dest),(dest,aux1),(aux1,aux2),(aux2,start)}"
"""
import re
import sys
from functools import lru_cache
from itertools import permutations, product

INF = float("inf")
ABBR = {"start": "S", "dest": "D", "aux1": "A1", "aux2": "A2"}


# =========================== input ===========================

def parse_v(text):
    return [w.lower() for w in re.findall(r"[A-Za-z_]\w*", text) if w.lower() != "v"]


def parse_e(text):
    return [(a.lower(), b.lower())
            for a, b in re.findall(r"\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*\)", text)]


def short(p):
    return ABBR.get(p, p.upper())


# =========================== solver ===========================

class Graph:
    def __init__(self, pegs, edges):
        self.pegs, self.edges = pegs, set(edges)
        self.cost = lru_cache(None)(self._cost)

    def paths(self, s, d):
        out, others = [], [p for p in self.pegs if p not in (s, d)]
        for r in range(len(others) + 1):
            for mid in permutations(others, r):
                path = (s,) + mid + (d,)
                if all((path[i], path[i + 1]) in self.edges for i in range(len(path) - 1)):
                    out.append(path)
        return out

    def _cost(self, n, s, d):
        """fewest moves for n disks s -> d (used only to check feasibility)"""
        if n == 0 or s == d:
            return 0
        best = INF
        for path in self.paths(s, d):
            states = {s: 0}
            for u, v in zip(path, path[1:]):
                nxt = {}
                for loc, c in states.items():
                    for w in self.pegs:
                        if w not in (u, v):
                            c2 = c + self.cost(n - 1, loc, w) + 1
                            nxt[w] = min(nxt.get(w, INF), c2)
                states = nxt
            for loc, c in states.items():
                best = min(best, c + self.cost(n - 1, loc, d))
        return best

    def ok(self, s, d):
        return self.cost(5, s, d) < INF

    def plans(self, s, d):
        """every way to move a tower s -> d: big disk path + parking peg per hop"""
        out = set()
        for path in self.paths(s, d):
            hops = list(zip(path, path[1:]))
            choices = [[w for w in self.pegs if w not in hop] for hop in hops]
            for parks in product(*choices):
                steps, loc, good = [], s, True
                for (u, v), w in zip(hops, parks):
                    if loc != w:
                        if not self.ok(loc, w):
                            good = False
                            break
                        steps.append(("call", loc, w))
                    steps.append(("move", u, v))
                    loc = w
                if good and loc != d:
                    if self.ok(loc, d):
                        steps.append(("call", loc, d))
                    else:
                        good = False
                if good:
                    out.add(tuple(steps))
        return list(out)


def best_algorithm(G, s, d):
    """Pick plans so the algorithm uses as FEW functions as possible
    (then fewest calls per function, then fewest moves)."""
    cache = {}

    def plans(pair):
        if pair not in cache:
            cache[pair] = G.plans(*pair)
        return cache[pair]

    def evaluate(assign):
        @lru_cache(None)
        def T(n, pair):
            if n == 0:
                return 0
            return sum(1 if k == "move" else T(n - 1, (a, b)) for k, a, b in assign[pair])
        r = max(sum(1 for k, *_ in st if k == "call") for st in assign.values())
        return (len(assign), r, T(8, (s, d)))

    best = [None, None]

    def dfs(assign, pending):
        pending = [p for p in pending if p not in assign]
        uniq = list(dict.fromkeys(pending))
        if best[0] and len(assign) + len(uniq) > best[0][0]:
            return
        if not uniq:
            score = evaluate(assign)
            if best[0] is None or score < best[0]:
                best[0], best[1] = score, dict(assign)
            return
        pair = uniq[0]
        opts = plans(pair)
        opts.sort(key=lambda st: (len({(a, b) for k, a, b in st if k == "call"} - set(assign) - {pair}),
                                  sum(1 for k, *_ in st if k == "call"), len(st)))
        for st in opts:
            assign[pair] = st
            new = [(a, b) for k, a, b in st if k == "call"]
            dfs(assign, uniq[1:] + new)
            del assign[pair]

    dfs({}, [(s, d)])
    return best[1]


def simulate(assign, n, s, d, edges, pegs):
    seq = []

    def go(n, pair):
        if n == 0:
            return
        for k, a, b in assign[pair]:
            if k == "move":
                seq.append((n, a, b))
            else:
                go(n - 1, (a, b))
    go(n, (s, d))
    st = {p: [] for p in pegs}
    st[s] = list(range(n, 0, -1))
    for disk, u, v in seq:
        assert (u, v) in edges, f"illegal move {u}->{v}"
        assert st[u] and st[u][-1] == disk, "disk not on top"
        assert not st[v] or st[v][-1] > disk, "big disk on small disk"
        st[v].append(st[u].pop())
    assert st[d] == list(range(n, 0, -1))
    return seq


# =========================== drawing ===========================
# Pegs go on a diamond:  top, right, bottom, left.
# start is placed on the left; the rest are arranged so that as many
# arrows as possible go around the outside (like drawing it by hand).

def layout(pegs, edges, start, dest):
    others = [p for p in pegs if p != start]
    ring = ["top", "right", "bottom", "left"]
    adj = {frozenset(x) for x in [("top", "right"), ("right", "bottom"),
                                  ("bottom", "left"), ("left", "top")]}
    best = None
    for perm in permutations(others, 3):
        pos = {start: "left", perm[0]: "top", perm[1]: "right", perm[2]: "bottom"}
        outside = sum(frozenset((pos[a], pos[b])) in adj for a, b in edges)
        clockwise = sum((ring.index(pos[b]) - ring.index(pos[a])) % 4 == 1 for a, b in edges)
        score = (outside, clockwise, pos[dest] == "bottom")
        if best is None or score > best[0]:
            best = (score, pos)
    return best[1]


def draw(pegs, edges, start, dest):
    if len(pegs) != 4:
        return ["  (drawing supports exactly 4 pegs)"]
    pos = layout(pegs, edges, start, dest)
    at = {v: k for k, v in pos.items()}
    W, H = 41, 9
    g = [[" "] * W for _ in range(H)]

    def put(r, c, s):
        for i, ch in enumerate(s):
            g[r][c + i] = ch

    lab = {k: short(v) for k, v in at.items()}
    put(0, 20 - len(lab["top"]) // 2, lab["top"])
    put(8, 20 - len(lab["bottom"]) // 2, lab["bottom"])
    put(4, 8 - len(lab["left"]), lab["left"])
    put(4, 33, lab["right"])

    # each side: cells from end A to end B, the line char, arrowhead at A, arrowhead at B
    sides = {
        frozenset(("left", "top")):     ("left", [(3, 10), (2, 12), (1, 14)], "/", "↙", "↗"),
        frozenset(("top", "right")):    ("top", [(1, 26), (2, 28), (3, 30)], "\\", "↖", "↘"),
        frozenset(("right", "bottom")): ("right", [(5, 30), (6, 28), (7, 26)], "/", "↗", "↙"),
        frozenset(("bottom", "left")):  ("bottom", [(7, 14), (6, 12), (5, 10)], "\\", "↘", "↖"),
        frozenset(("top", "bottom")):   ("top", [(r, 20) for r in range(1, 8)], "|", "↑", "↓"),
        frozenset(("left", "right")):   ("left", [(4, c) for c in range(10, 31)], "-", "←", "→"),
    }
    for a, b in edges:
        pa, pb = pos[a], pos[b]
        endA, cells, ch, headA, headB = sides[frozenset((pa, pb))]
        for r, c in cells:
            if g[r][c] in "|-" and g[r][c] != ch:
                g[r][c] = "+"
            elif g[r][c] == " ":
                g[r][c] = ch
        if pb == endA:              # arrow points at end A
            r, c = cells[0]
            g[r][c] = headA
        else:
            r, c = cells[-1]
            g[r][c] = headB
    return ["    " + "".join(row).rstrip() for row in g]


# =========================== output ===========================

ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def fn(a, b):
    return f"F_{short(a)}_{short(b)}"


def run(pegs, edges, start, dest):
    for a, b in edges:
        for p in (a, b):
            if p not in pegs:
                pegs.append(p)
    G = Graph(pegs, edges)

    bar = "=" * 60
    print(bar)
    print("  GRAPH")
    print(bar)
    print("  v = {" + ", ".join(pegs) + "}")
    print("  e = {" + ", ".join(f"({a}, {b})" for a, b in edges) + "}")
    print("  " + "   ".join(f"{short(p)} = {p}" for p in pegs))
    print()
    for line in draw(pegs, edges, start, dest):
        print(line)
    print()

    if not G.ok(start, dest):
        print(f"  {start} -> {dest} is impossible with 2+ disks on this graph.")
        return

    assign = best_algorithm(G, start, dest)
    order, todo = [], [(start, dest)]
    while todo:
        p = todo.pop(0)
        if p in order:
            continue
        order.append(p)
        todo += [(a, b) for k, a, b in assign[p] if k == "call"]

    print(bar)
    print("  ALGORITHM")
    print(bar)
    print("  Rule: before disk n moves X -> Y, disks 1..n-1 must sit")
    print("        on a peg that is neither X nor Y.")
    for a, b in order:
        steps = assign[(a, b)]
        moves_only = [(u, v) for k, u, v in steps if k == "move"]
        path = [moves_only[0][0]] + [v for _, v in moves_only]
        print()
        print(f"  def {fn(a, b)}(n) {{                // n disks  {short(a)} -> {short(b)}")
        print()
        print(f"      if (n == 1) {{ move disk {'  ->  '.join(short(p) for p in path)} }}"
              f"   -> base case")
        print(f"      else")
        print()
        call_no = 0
        for k, u, v in steps:
            if k == "call":
                call_no += 1
                print(f"          {fn(u, v)}(n-1);")
                print(f"              move n-1 disks from {short(u)} to {short(v)}")
                print(f"              // {ORD.get(call_no, str(call_no) + 'th')} recursive call")
                print()
            else:
                print(f"          move disk n  {short(u)} -> {short(v)};")
                print()
        print("  }")
    print()
    print(f"  Solve the problem:  {fn(start, dest)}(n)")
    print()

    # ---------- complexity ----------
    calls = {p: sum(1 for k, *_ in assign[p] if k == "call") for p in order}
    r = max(calls.values())
    worst = next(p for p in order if calls[p] == r)

    @lru_cache(None)
    def T(n, pair):
        if n == 0:
            return 0
        return sum(1 if k == "move" else T(n - 1, (a, b)) for k, a, b in assign[pair])

    print(bar)
    print("  TIME COMPLEXITY")
    print(bar)
    print("  Recurrences (T = number of moves):")
    for p in order:
        terms = [f"T_{short(a)}_{short(b)}(n-1)" for k, a, b in assign[p] if k == "call"]
        mv = sum(1 for k, *_ in assign[p] if k == "move")
        print(f"      T_{short(p[0])}_{short(p[1])}(n) = " + " + ".join(terms + [str(mv)]))
    print()
    print(f"  r = {r}      most recursive calls in one function ({fn(*worst)})")
    print(f"  d = 1      each call is on n-1 disks (size drops by 1)")
    print()
    print(f"      T(n) = {r}·T(n-1) + c")
    print(f"           = {r}^2·T(n-2) + ({r}+1)c")
    print(f"           = ...")
    print(f"           = {r}^n·T(0) + c·({r}^n - 1)/{max(r - 1, 1)}")
    print()
    print(f"  Decreasing master theorem: T(n) = r·T(n-d) + c  =>  O(r^(n/d)) = O({r}^(n/1))")
    print()
    print(f"      Time complexity is   O({r}^n)" if r > 1 else "      Time complexity is   O(n)")
    print()

    # ---------- check ----------
    for n in range(1, 7):
        simulate(assign, n, start, dest, G.edges, pegs)
    print(bar)
    print("  CHECK")
    print(bar)
    print("  moves needed:  " + ",  ".join(f"n={n}: {T(n, (start, dest))}" for n in range(1, 7)))
    for n in (1, 2):
        seq = simulate(assign, n, start, dest, G.edges, pegs)
        print(f"  n = {n}:  " + ",  ".join(f"disk{dk} {short(u)}->{short(v)}" for dk, u, v in seq))
    print("  Every move simulated for n = 1..6: all legal.")


def main():
    if len(sys.argv) >= 3:
        vtxt, etxt = sys.argv[1], sys.argv[2]
    else:
        vtxt = input("v = ")
        etxt = input("e = ")
    pegs, edges = parse_v(vtxt), parse_e(etxt)
    if not edges:
        sys.exit("Couldn't read any edges. Write them like (start, dest), (dest, aux1)")
    for a, b in edges:
        for p in (a, b):
            if p not in pegs:
                pegs.append(p)
    start = "start" if "start" in pegs else input(f"start peg? {pegs}: ").strip().lower()
    dest = "dest" if "dest" in pegs else input(f"destination peg? {pegs}: ").strip().lower()
    print()
    run(pegs, edges, start, dest)


if __name__ == "__main__":
    main()