---
description: Health-check the wiki (broken links, orphans, missing citations, contradictions, index gaps)
allowed-tools: Read, Glob, Grep, Edit
---

You are the librarian doing maintenance. First read `CLAUDE.md`.

Audit the `wiki/` tree and report problems. Check, at minimum:
1. **Broken wikilinks** — `[[targets]]` that have no matching page.
2. **Orphan pages** — pages in `wiki/` with no incoming links from any other page.
3. **Missing citations** — wiki pages without a `## Source(s)` section.
4. **Unresolved contradictions** — `## Contradictions` sections still open.
5. **Index gaps** — pages not listed in `wiki/index.md`.
6. **Slug/convention drift** — filenames not following the lowercase-hyphen rule.

Output a structured report grouped by category, each finding with the file path and a suggested fix.
Propose fixes but only apply safe, mechanical ones (e.g. creating an obvious stub, adding a page to the index).
For anything judgment-heavy (resolving a contradiction, merging pages), list it for the human to confirm.
Append one entry to `wiki/log.md` (operation `lint`, counts per category). Never touch `raw/` or legacy folders.
