```markdown
# COSC 3320 Exam 1 — Terminal Scripts Guide

This guide details how to execute and extract full-credit answers from your four exam automation scripts:
* `Hanoi.py`[cite: 44, 47]
* `vm_pages.py`[cite: 47]
* `quicksort_builder.py`[cite: 47]
* `matrix_chain.py`[cite: 47]

---

## 1. Problem 1: Directed Towers of Hanoi (`Hanoi.py`)

Solves the restricted Towers of Hanoi problem on a directed graph[cite: 1, 44]. It outputs the mutual recursion algorithm, ASCII diagram, recurrence relation, and decreasing Master Theorem complexity[cite: 44].

### Running the Script

#### Option A: One-Line CLI Execution (Recommended)
Pass the vertex set $V$ and edge set $E$ inside quotes directly as arguments[cite: 44]:
```bash
python3 Hanoi.py "{Start, Aux1, Aux2, Dest}" "{(Start, Aux1), (Aux1, Aux2), (Aux2, Dest), (Dest, Start)}"

```

#### Option B: Interactive Mode

```bash
python3 Hanoi.py

```

* **Prompt 1 (`v = `):** `{Start, Aux1, Aux2, Dest}`

* **Prompt 2 (`e = `):** `{(Start, Aux1), (Aux1, Aux2), (Aux2, Dest), (Dest, Start)}`


### What to Write on Your Exam Paper

1. **The Code:** Copy every generated `def F_...` function from the `ALGORITHM` block verbatim, including the base cases and inline comments (e.g., `// 1st recursive call`).


2. **The Derivation:** Copy the exact recurrence and Master Theorem text:



$$T(n) = 3 \cdot T(n - 1) + c$$



$$\text{By decreasing Master Theorem } (r = 3, d = 1): O(r^{n/d}) = O(3^n)$$




---

## 2. Problem 2: Virtual Memory LRU Page Faults (`vm_pages.py`)

Calculates page transfers between disk and main memory under LRU replacement for the nested array loop:

```pascal
for I := 1 to N do
    for J := 1 to N do
        A[J, I] := A[J, I] * B[I, J]

```

### Running the Script

#### Option A: One-Line CLI Execution (Recommended)

Arguments order: `N` (matrix dimension), `P` (page size), `M` (memory page limit), `A_layout`, `B_layout`:

```bash
python3 vm_pages.py 2048 1024 1024 row row

```

#### Option B: Interactive Mode

```bash
python3 vm_pages.py

```

* **Array dimension N [2048]:** `2048`

* **Words per page P [1024]:** `1024`

* **Active memory limit M [1024]:** `1024`

* **Array A layout (row/col) [row]:** `row`

* **Array B layout (row/col) [row]:** `row`


### What to Write on Your Exam Paper

1. **Pages per Vector:** $\frac{N}{P} = \frac{2048}{1024} = 2\text{ pages per row}$.


2. **Access Analysis:**
* Matrix $B[I, J]$: Accessed sequentially across row $I \implies \frac{N}{P} = 2\text{ reads}$ per outer loop iteration.


* Matrix $A[J, I]$: Strided column access touches $N = 2048$ distinct pages. Because $M < N$, LRU thrashes completely, requiring $2048\text{ reads} + 2048\text{ writes}$.




3. **Calculation:**

$$\text{Transfers per } I \text{ loop} = 2 + 2048 + 2048 = 4098\text{ transfers}$$



$$\text{Total Transfers} = 2048 \times 4098 = \mathbf{8{,}392{,}704}$$




---

## 3. Problem 3: QuickSort Array Constructor (`quicksort_builder.py`)

Generates optimal $O(n \log n)$ arrays (equal splits) and slowest $O(n^2)$ arrays for any pivot rule specified in the prompt.

### Running the Script

#### Option A: One-Line CLI Execution (Recommended)

Arguments order: `n` (array size), `pivot_rule` (`lo`, `lo+1`, `hi`, or `mid`):

```bash
python3 quicksort_builder.py 15 lo

```

(Use `lo+1` if the exam specifies the second element $A[\text{lo}+1]$)

#### Option B: Interactive Mode

```bash
python3 quicksort_builder.py

```

* **Enter array size n [15]:** `15`

* **Pivot selection rule [lo]:** `lo`


### What to Write on Your Exam Paper

1. **Part (a) Optimal Array ($n = 15$, pivot $A[\text{lo}]$):**

* **Array:** `8, 4, 2, 1, 3, 6, 5, 7, 12, 10, 9, 11, 14, 13, 15`

* **Explanation:** QuickSort executes optimally when every chosen pivot is the median of the active subarray, dividing remaining elements into two equal-sized partitions at every recursive level. Arranging the median at index `lo` guarantees balanced splits of sizes $7/7$, then $3/3$, then $1/1$, giving $O(n \log n)$.




2. **Part (b) Slowest Array:**

* **Array:** `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15`

* **Explanation:** A pre-sorted array causes the first element ($A[\text{lo}]$) to always pick the extreme minimum, yielding unbalanced partitions of size $0$ and $k-1$. This maximizes recursion depth to $n$, requiring $\sum k = O(n^2)$ operations.





---

## 4. Problem 4: Matrix Chain Multiplication DP (`matrix_chain.py`)

Computes the dynamic programming table for matrix chain multiplication, finding the worst-case (maximum), best-case (minimum), or average scalar multiplications.

### Running the Script

#### Option A: One-Line CLI Execution (Recommended)

You can provide either the matrix labels or space-separated dimension scalars:

```bash
python3 matrix_chain.py "M_{9,3} * M_{3,9} * M_{9,1} * M_{1,8} * M_{8,4}" max

```


*Or using the 6 dimension scalars directly:*

```bash
python3 matrix_chain.py "9 3 9 1 8 4" max

```

#### Option B: Interactive Mode

```bash
python3 matrix_chain.py

```

* **Product or dimensions:** `9 3 9 1 8 4`

* **Mode (max / min / avg) [max]:** `max`


### What to Write on Your Exam Paper

1. **Recurrence Formula:**

$$S[i, j] = \max_{i \le k < j} \{ S[i, k] + S[k+1, j] + p_{i-1} \cdot p_k \cdot p_j \} \quad \text{with } S[i, i] = 0$$



2. **Intermediate Diagonal Calculations:** Copy the arithmetic lines printed under `Chains of Length L = 2, 3, 4, 5` showing each candidate split $k$.


3. **The DP Table:** Copy the upper-triangular grid printed under `COMPLETED DYNAMIC PROGRAMMING TABLE`.


4. **Final Deliverable & Check:**
* Write the parenthesization string: `(((M_9,3 * M_3,9) * (M_9,1 * M_1,8)) * M_8,4)`

* Copy the step-by-step cost verification table summing to **1251** scalar multiplications.





```

```
