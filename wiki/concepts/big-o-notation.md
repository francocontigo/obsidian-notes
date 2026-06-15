# Big-O Notation

A measure of how an algorithm **scales** with input size — for both time and space complexity. It describes
scaling, not absolute performance.

## Classes (fastest → slowest)
- **O(1)** — constant: same cost regardless of input (e.g. reading the first element of an [[array]]).
- **O(log n)** — doubling the input does not double the cost.
- **O(n)** — linear: cost grows with input size.
- **O(n log n)** — typical of sorting and divide-and-conquer.
- **O(n²)** — nested loops (loop inside a loop).
- **O(2ⁿ)**, **O(√n)**, **O(n!)** — higher-order classes.

## Related
[[linked-list]] · [[hash-map]] · [[array]] · [[data-structures-complexity]]

## Source(s)
- `1 Books&Courses/Estrutura de Dados e Algoritmos Augusto Galego.md`

## Recall
- **Q:** Order from fastest to slowest growth: O(n²), O(1), O(n log n), O(log n), O(n). — **A:** O(1) < O(log n) < O(n) < O(n log n) < O(n²)
- **Q:** A loop inside a loop over the same input is which class? — **A:** O(n²)
