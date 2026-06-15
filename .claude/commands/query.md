---
description: Answer a question from the wiki and save the report to output/
argument-hint: <your question>
allowed-tools: Read, Glob, Grep, Write
---

You are answering from this second brain. First read `CLAUDE.md`.

Question: `$ARGUMENTS`

1. Load the relevant wiki pages. Start from `wiki/index.md`, then Glob/Grep across `wiki/` to pull every page
   that bears on the question. No RAG — read the actual markdown (it fits in context).
2. Answer thoroughly and concretely. **Cite the wiki pages you used** as `[[wikilinks]]` inline.
3. If the wiki lacks the information, say so plainly and suggest what to `/ingest` to fill the gap. Do not invent facts.
4. Save the full answer to `output/<slug-of-question>.md` with a `## Sources` section listing the pages used,
   and print a short version to the console.

Do not modify any wiki or raw page during a query.
