# Hash Map

Key-value structure (a `dict` in Python). Maps keys to slots via a hash function.

## Core ideas
- **Hash function** — turns a key into a bucket index.
- **Load factor** — ratio of stored entries to buckets; drives resizing.
- **Collisions** — distinct keys hashing to the same bucket; must be resolved.

## Related
[[big-o-notation]] · [[data-structures-complexity]]

## Source(s)
- `1 Books&Courses/Estrutura de Dados e Algoritmos Augusto Galego.md`

## Recall
- **Q:** Name the three core ideas behind a hash map. — **A:** Hash function (key→bucket), load factor (entries/buckets), collisions (distinct keys, same bucket).
