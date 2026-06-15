"""Local embeddings + reranking via sentence-transformers (offline, no API key).

Models are loaded lazily and memoized so the heavy torch import only happens
when semantic search / rerank is actually requested.
"""
from __future__ import annotations

import functools

EMBED_MODEL = "all-MiniLM-L6-v2"                       # small, fast, local
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # cross-encoder reranker


@functools.lru_cache(maxsize=1)
def _embedder(name: str = EMBED_MODEL):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


@functools.lru_cache(maxsize=1)
def _reranker(name: str = RERANK_MODEL):
    from sentence_transformers import CrossEncoder
    return CrossEncoder(name)


def embed(texts: list[str]):
    """Return L2-normalized embeddings (numpy array) so dot product == cosine."""
    return _embedder().encode(texts, normalize_embeddings=True, show_progress_bar=False)


def rerank(query: str, passages: list[str]):
    """Return a relevance score per passage from the cross-encoder."""
    return _reranker().predict([(query, p) for p in passages])


def available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
        return True
    except Exception:
        return False
