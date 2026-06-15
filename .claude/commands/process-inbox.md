---
description: Triage raw/inbox.md fleeting notes into the wiki
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch
---

You are the librarian for this second brain. First read `CLAUDE.md` and follow its hard rules.

Drain the capture inbox at `raw/inbox.md`. Each non-empty, non-comment line (or block separated by `---`)
is one fleeting item: an idea, a todo, a link, or a quick note.

For each item, top to bottom:
1. Decide its kind: a **link/URL** → ingest like `/ingest` (summarize + extract). A **fact/idea/note** →
   route it to the right `wiki/` page (entities/concepts/synthesis), creating stubs and `[[wikilinks]]` as needed.
   A pure **todo/reminder** with no knowledge value → leave it in the inbox (this system is a knowledge base,
   not a task manager) and say so in your report.
2. Cite the inbox as the source on any page you create (`## Source(s): raw/inbox.md`). On any new/expanded
   `concepts/` or `synthesis/` page, add a `## Recall` section and enqueue its cards in `review/queue.md`
   (`box: 1`, `due: <current session>`), per the Learning layer rules in `CLAUDE.md`.
3. Once an item is integrated, **remove that line from `raw/inbox.md`**. Keep items you intentionally left.

Then: update `wiki/index.md` and append ONE summary entry to `wiki/log.md` (operation `process-inbox`,
how many items processed/left, pages touched).

Print a short report: items processed, items left in inbox (with why), pages created/updated.
