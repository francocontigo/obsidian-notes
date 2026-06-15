"""RAG orchestration: retrieve from wiki/ with HybridSearch, then answer with the
selected provider. Returns the answer, its perplexity (OpenAI only), and sources.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import llm
from .search import Hit

SYSTEM = (
    "You are a retrieval-grounded assistant for a personal knowledge base (a 'second brain').\n"
    "Answer ONLY from the provided context passages. If the answer isn't in the context, say so "
    "plainly and suggest what to ingest. Cite the passages you use by their [[wikilink]] page name. "
    "Be concise and concrete."
)


@dataclass
class RagResult:
    answer: str
    perplexity: float | None
    note: str | None
    hits: list[Hit]


def _context(hits: list[Hit]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        page = h.chunk.rel_path
        blocks.append(f"[{i}] source: {page}  (section: {h.chunk.heading})\n{h.chunk.text}")
    return "\n\n---\n\n".join(blocks)


def answer(question: str, hits: list[Hit], cfg: llm.LLMConfig) -> RagResult:
    user = (
        f"Context passages:\n\n{_context(hits)}\n\n"
        f"Question: {question}\n\n"
        "Answer from the context above and cite pages as [[page-name]]."
    )
    gen = llm.generate(SYSTEM, user, cfg)
    return RagResult(answer=gen.text, perplexity=gen.perplexity, note=gen.note, hits=hits)
