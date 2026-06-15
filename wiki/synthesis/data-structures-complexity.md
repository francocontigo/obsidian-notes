# Synthesis: Data Structures & Their Complexity

A cross-cutting view of the core data structures and their costs, using [[big-o-notation]].

| Structure | Read | Insert | Delete | Notes |
|---|---|---|---|---|
| [[array]] | O(1) | — | — | contiguous memory |
| [[linked-list]] | O(1)–O(n) | O(1)–O(n) | O(1)–O(n) | best at head/tail, worst needs traversal |
| [[hash-map]] | ~O(1) avg | ~O(1) avg | ~O(1) avg | degrades with collisions / load factor |
| [[queue]] (FIFO) | — | O(1) | O(1) | first in, first out |
| stack (LIFO) | — | O(1) | O(1) | last in, first out |

Not yet detailed in the source: binary tree, heap, graphs, trie — candidates for future ingestion.

## Related
[[big-o-notation]] · [[estrutura-de-dados-augusto-galego]]

## Source(s)
- `1 Books&Courses/Estrutura de Dados e Algoritmos Augusto Galego.md`
