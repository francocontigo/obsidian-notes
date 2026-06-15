# Review Queue (spaced repetition — Leitner)

session: 0

Leitner intervals in **sessions**: box 1→1, 2→2, 3→4, 4→8, 5→16. Correct = box+1 (max 5); wrong = box 1.
`/study` increments `session` and reviews every card with `due <= session`. Maintained by Claude.

---

## Card: big-o-growth-order
- page: [[big-o-notation]]
- box: 1
- due: 0
- Q: Order from fastest to slowest growth: O(n²), O(1), O(n log n), O(log n), O(n).
- A: O(1) < O(log n) < O(n) < O(n log n) < O(n²)

## Card: big-o-nested-loops
- page: [[big-o-notation]]
- box: 1
- due: 0
- Q: A loop inside a loop over the same input is which complexity class?
- A: O(n²)

## Card: array-read-cost
- page: [[array]]
- box: 1
- due: 0
- Q: What is the read cost of an array, and why?
- A: O(1) — contiguous memory allows direct index access.

## Card: linked-list-costs
- page: [[linked-list]]
- box: 1
- due: 0
- Q: Give best and worst case for read/insert/delete on a linked list.
- A: All are best O(1), worst O(n) (worst requires traversal; insert is O(1) at head/tail).

## Card: hash-map-pieces
- page: [[hash-map]]
- box: 1
- due: 0
- Q: Name the three core ideas behind a hash map.
- A: Hash function (key→bucket), load factor (entries/buckets), collisions (distinct keys, same bucket).

## Card: queue-vs-stack
- page: [[queue]]
- box: 1
- due: 0
- Q: Queue vs stack — which is FIFO and which is LIFO?
- A: Queue = FIFO (First In First Out); Stack = LIFO (Last In First Out).

## Card: sql-elements
- page: [[sql-language-elements]]
- box: 1
- due: 0
- Q: What does a SQL predicate evaluate to?
- A: True, false, or unknown.

## Card: sql-constraints
- page: [[database-integrity]]
- box: 1
- due: 0
- Q: Why are constraints used sparingly, and what's the most common one?
- A: They burden the DBMS; the most common is NOT NULL.

## Card: sql-sequences
- page: [[database-integrity]]
- box: 1
- due: 0
- Q: What do sequences guarantee, and what are they typically used for?
- A: Continuity and uniqueness; typically used as identifiers.
