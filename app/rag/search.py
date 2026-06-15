"""Hybrid search engine: BM25 (lexical) + embeddings (semantic), fused with
Reciprocal Rank Fusion, then optionally reranked by a cross-encoder.

Degrades gracefully: if sentence-transformers isn't installed, it runs BM25-only
and reports that in `.modes`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import embed
from .chunk import Chunk

_RRF_K = 60  # standard RRF dampening constant


@dataclass
class Hit:
    chunk: Chunk
    score: float
    bm25_rank: int | None = None
    sem_rank: int | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class HybridSearch:
    def __init__(self, chunks: list[Chunk], use_semantic: bool = True, use_rerank: bool = True):
        self.chunks = chunks
        self.modes: list[str] = []
        self._texts = [c.text for c in chunks]

        # Lexical index (BM25). Required.
        from rank_bm25 import BM25Okapi
        self._bm25 = BM25Okapi([_tokenize(t) for t in self._texts])
        self.modes.append("bm25")

        # Semantic index (embeddings). Optional.
        self._emb = None
        self.use_semantic = use_semantic and embed.available() and len(chunks) > 0
        if self.use_semantic:
            try:
                self._emb = embed.embed(self._texts)
                self.modes.append("semantic")
            except Exception:
                self.use_semantic = False

        self.use_rerank = use_rerank and embed.available() and len(chunks) > 0
        if self.use_rerank:
            self.modes.append("rerank")

    def search(self, query: str, k: int = 8, candidates: int = 24) -> list[Hit]:
        if not self.chunks:
            return []

        # 1) Lexical ranking
        bm25_scores = self._bm25.get_scores(_tokenize(query))
        bm25_order = sorted(range(len(self.chunks)), key=lambda i: bm25_scores[i], reverse=True)
        bm25_rank = {idx: r for r, idx in enumerate(bm25_order)}

        # 2) Semantic ranking
        sem_rank: dict[int, int] = {}
        if self.use_semantic and self._emb is not None:
            import numpy as np
            qv = embed.embed([query])[0]
            sims = np.asarray(self._emb) @ np.asarray(qv)
            sem_order = sorted(range(len(self.chunks)), key=lambda i: sims[i], reverse=True)
            sem_rank = {idx: r for r, idx in enumerate(sem_order)}

        # 3) Reciprocal Rank Fusion over whichever rankings exist
        fused: dict[int, float] = {}
        for idx in range(len(self.chunks)):
            s = 1.0 / (_RRF_K + bm25_rank[idx])
            if sem_rank:
                s += 1.0 / (_RRF_K + sem_rank[idx])
            fused[idx] = s
        ranked = sorted(fused, key=lambda i: fused[i], reverse=True)[:candidates]

        hits = [
            Hit(chunk=self.chunks[i], score=fused[i],
                bm25_rank=bm25_rank.get(i), sem_rank=sem_rank.get(i))
            for i in ranked
        ]

        # 4) Cross-encoder rerank of the fused candidate set
        if self.use_rerank and hits:
            try:
                scores = embed.rerank(query, [h.chunk.text for h in hits])
                for h, sc in zip(hits, scores):
                    h.score = float(sc)
                hits.sort(key=lambda h: h.score, reverse=True)
            except Exception:
                pass

        return hits[:k]
