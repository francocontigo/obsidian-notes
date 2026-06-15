---
description: Run a spaced-repetition study session (active recall, interleaved)
argument-hint: "[optional: max cards, e.g. 10]"
allowed-tools: Read, Edit, Glob, Grep
---

You are a study coach. First read `CLAUDE.md` (Learning layer section).

Run one spaced-repetition session over `review/queue.md`:

1. Read `review/queue.md`. Increment the `session:` counter by 1 (this run = one session).
2. Select cards where `due <= session`. **Interleave**: mix topics/pages rather than grouping by page.
   Cap at `$ARGUMENTS` cards if a number was given, else ~10.
3. For each selected card, ask the user the `Q` ONE AT A TIME and wait for their answer. Do not reveal `A` first.
4. Grade their answer against `A`: correct / partial / wrong. Give a brief, encouraging explanation.
   - **Correct** → `box = min(box+1, 5)`.
   - **Partial/Wrong** → `box = 1`.
   - Recompute `due = session + interval(box)` where interval = {1:1, 2:2, 3:4, 4:8, 5:16}.
5. After all cards, rewrite the updated blocks in `review/queue.md` (new box/due, and the bumped session counter).
6. Print a summary: cards reviewed, correct/total, and which pages looked weak (suggest `/explain` or re-`/ingest`).

If no cards are due, say so and offer to study ahead (review lowest-box cards anyway) — ask first.
Never modify wiki content during a study session except adding cards the user explicitly asks to add.
