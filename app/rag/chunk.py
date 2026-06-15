"""Split wiki/ markdown into retrievable chunks (one per heading section)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    rel_path: str    # vault-relative, e.g. "wiki/concepts/big-o-notation.md"
    title: str       # page H1 (or filename)
    heading: str     # section heading this chunk belongs to
    text: str        # the chunk body (heading + content)


def load_chunks(wiki_dir: Path, vault_root: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for p in sorted(wiki_dir.rglob("*.md")):
        if p.name == ".gitkeep":
            continue
        rel = p.relative_to(vault_root).as_posix()
        raw = p.read_text(encoding="utf-8")
        title = _title(raw, p.stem)
        for heading, body in _sections(raw):
            text = (heading + "\n" + body).strip() if heading else body.strip()
            if text:
                chunks.append(Chunk(rel_path=rel, title=title, heading=heading or title, text=text))
    return chunks


def _title(raw: str, fallback: str) -> str:
    for line in raw.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _sections(raw: str) -> list[tuple[str, str]]:
    """Yield (heading, body) sections, splitting at any markdown heading line."""
    sections: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []
    for line in raw.splitlines():
        if line.lstrip().startswith("#"):
            if heading or body:
                sections.append((heading, "\n".join(body)))
            heading = line.lstrip("#").strip()
            body = []
        else:
            body.append(line)
    if heading or body:
        sections.append((heading, "\n".join(body)))
    return sections
