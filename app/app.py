"""
Second Brain — Streamlit interface.

An optional GUI layer ON TOP of the Claude Code CLI. The LLM still does all the
knowledge work (ingest / query / lint); this app just makes it point-and-click and
gives you a reader for the wiki. Everything stays plain markdown on disk.

Run:  streamlit run app/app.py     (or `make ui` / `./sb.ps1 ui`)
Requires: `claude` CLI on PATH, and `pip install -r app/requirements.txt`.
Cross-platform: pure Python + subprocess, no shell-specific calls.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import streamlit as st

# Make the `rag` package importable regardless of the launch directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Vault root = parent of this app/ folder. Keeps every path vault-relative.
VAULT = Path(__file__).resolve().parent.parent
RAW_INBOX = VAULT / "raw" / "inbox.md"
WIKI = VAULT / "wiki"
OUTPUT = VAULT / "output"
LOG = WIKI / "log.md"
QUEUE = VAULT / "review" / "queue.md"

# Leitner intervals (in sessions) per box — same scheme as CLAUDE.md / the /study command.
INTERVALS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}

CLAUDE = os.environ.get("CLAUDE") or shutil.which("claude") or "claude"
PERM = ["--permission-mode", "acceptEdits"]


def run_claude(prompt: str) -> tuple[int, str]:
    """Invoke the Claude Code CLI headlessly from the vault root."""
    try:
        proc = subprocess.run(
            [CLAUDE, "-p", prompt, *PERM],
            cwd=VAULT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError:
        return 1, f"`claude` CLI not found (looked for: {CLAUDE}). Install Claude Code or set $CLAUDE."
    except subprocess.TimeoutExpired:
        return 1, "Timed out after 600s."


def wiki_pages() -> list[Path]:
    return sorted(p for p in WIKI.rglob("*.md") if p.name != ".gitkeep")


# --- Hybrid search index (built from wiki/, cached until files change) ---

def _wiki_signature() -> tuple:
    return tuple(sorted(
        (str(p), p.stat().st_mtime)
        for p in WIKI.rglob("*.md") if p.name != ".gitkeep"
    ))


@st.cache_resource(show_spinner="Building search index…")
def get_search_index(signature: tuple, use_semantic: bool, use_rerank: bool):
    from rag.chunk import load_chunks
    from rag.search import HybridSearch
    chunks = load_chunks(WIKI, VAULT)
    return HybridSearch(chunks, use_semantic=use_semantic, use_rerank=use_rerank)


# --- Spaced-repetition queue (deterministic; no LLM needed for scheduling) ---

def load_queue() -> tuple[str, int, list[dict]]:
    """Return (header_text, session, cards). header keeps the prose above the first card."""
    if not QUEUE.exists():
        return "", 0, []
    text = QUEUE.read_text(encoding="utf-8")
    session = int(re.search(r"^session:\s*(\d+)", text, re.M).group(1)) if re.search(r"^session:\s*(\d+)", text, re.M) else 0
    head, _, rest = text.partition("\n## Card:")
    cards = []
    for block in ("## Card:" + rest).split("## Card:")[1:] if rest else []:
        b = block.strip()
        def field(name):
            m = re.search(rf"^-\s*{name}:\s*(.+)$", b, re.M)
            return m.group(1).strip() if m else ""
        cards.append({
            "slug": b.splitlines()[0].strip(),
            "page": field("page"),
            "box": int(field("box") or 1),
            "due": int(field("due") or 0),
            "q": field("Q"),
            "a": field("A"),
        })
    return head.rstrip(), session, cards


def save_queue(header: str, session: int, cards: list[dict]) -> None:
    # Rebuild header with the updated session line, then re-render every card.
    header2 = re.sub(r"^session:\s*\d+", f"session: {session}", header, flags=re.M)
    parts = [header2.rstrip(), ""]
    for c in cards:
        parts.append(f"## Card: {c['slug']}")
        parts.append(f"- page: {c['page']}")
        parts.append(f"- box: {c['box']}")
        parts.append(f"- due: {c['due']}")
        parts.append(f"- Q: {c['q']}")
        parts.append(f"- A: {c['a']}")
        parts.append("")
    QUEUE.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def grade_card(card: dict, correct: bool, session: int) -> None:
    card["box"] = min(card["box"] + 1, 5) if correct else 1
    card["due"] = session + INTERVALS[card["box"]]


st.set_page_config(page_title="Second Brain", page_icon="🧠", layout="wide")
st.title("🧠 Second Brain")
st.caption("Karpathy LLM-Wiki pattern · markdown on disk · Claude is the librarian")

page = st.sidebar.radio("Section", ["Capture", "Ingest", "Study", "Ask", "Search", "Browse wiki", "Status"])

if page == "Capture":
    st.subheader("Quick capture → inbox")
    st.write("Fleeting thoughts go on top of `raw/inbox.md`. Drain them later with **Ingest → Process inbox**.")
    text = st.text_area("Thought / link / note", height=120, placeholder="An idea, a URL, a quick note…")
    if st.button("Append to inbox", type="primary", disabled=not text.strip()):
        old = RAW_INBOX.read_text(encoding="utf-8") if RAW_INBOX.exists() else ""
        RAW_INBOX.write_text(text.strip() + "\n" + old, encoding="utf-8")
        st.success("Captured to raw/inbox.md")

elif page == "Ingest":
    st.subheader("Ingest a source")
    src = st.text_input("File path (vault-relative) or URL", placeholder="1 Books&Courses/Descomplicando SQL.md")
    if st.button("Ingest", type="primary", disabled=not src.strip()):
        with st.spinner("Claude is reading and updating the wiki…"):
            code, out = run_claude(f"/ingest {src.strip()}")
        st.code(out or "(no output)")
        st.success("Done") if code == 0 else st.error(f"Exit code {code}")
    st.divider()
    st.subheader("Process inbox")
    if st.button("Process raw/inbox.md"):
        with st.spinner("Triaging inbox…"):
            code, out = run_claude("/process-inbox")
        st.code(out or "(no output)")

elif page == "Study":
    st.subheader("Study — spaced repetition")
    st.caption("Self-graded flashcards (deterministic Leitner). For free-text answers graded by Claude, use `make study`.")
    if not st.session_state.get("study_active"):
        header, session, cards = load_queue()
        due = [c for c in cards if c["due"] <= session + 1]
        st.write(f"Session counter: **{session}** · cards due this session: **{len(due)}** · total cards: {len(cards)}")
        if not cards:
            st.info("No cards yet. Ingest a source to generate recall cards.")
        else:
            if due:
                st.caption("Due: " + ", ".join(c["slug"] for c in due))
            if st.button("Start session", type="primary", disabled=not due):
                st.session_state.update(
                    study_active=True, study_header=header, study_session=session + 1,
                    study_cards=cards, study_due=[c["slug"] for c in due],
                    study_idx=0, study_reveal=False, study_correct=0,
                )
                st.rerun()
    else:
        cards = st.session_state.study_cards
        by_slug = {c["slug"]: c for c in cards}
        due_slugs = st.session_state.study_due
        idx = st.session_state.study_idx
        if idx >= len(due_slugs):
            save_queue(st.session_state.study_header, st.session_state.study_session, cards)
            st.success(f"Done — {st.session_state.study_correct}/{len(due_slugs)} correct. Queue saved (session {st.session_state.study_session}).")
            if st.button("Back to start"):
                for k in ["study_active", "study_idx", "study_reveal", "study_due", "study_cards", "study_session", "study_header", "study_correct"]:
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            card = by_slug[due_slugs[idx]]
            st.progress(idx / len(due_slugs), text=f"Card {idx + 1} of {len(due_slugs)}")
            st.caption(f"{card['page']} · box {card['box']}")
            st.markdown(f"### {card['q']}")
            if not st.session_state.study_reveal:
                if st.button("Reveal answer"):
                    st.session_state.study_reveal = True
                    st.rerun()
            else:
                st.info(card["a"])
                c1, c2 = st.columns(2)
                graded = None
                if c1.button("✅ Correct"):
                    graded = True
                if c2.button("❌ Wrong"):
                    graded = False
                if graded is not None:
                    grade_card(card, graded, st.session_state.study_session)
                    st.session_state.study_correct += int(graded)
                    st.session_state.study_idx += 1
                    st.session_state.study_reveal = False
                    st.rerun()

elif page == "Ask":
    st.subheader("Ask the wiki")
    q = st.text_input("Question", placeholder="what do my notes say about big-o for linked lists?")
    if st.button("Ask", type="primary", disabled=not q.strip()):
        with st.spinner("Answering from the wiki…"):
            code, out = run_claude(f"/query {q.strip()}")
        st.code(out or "(no output)")
        if OUTPUT.exists():
            latest = max((p for p in OUTPUT.glob("*.md")), key=lambda p: p.stat().st_mtime, default=None)
            if latest:
                st.divider()
                st.caption(f"Saved answer: output/{latest.name}")
                st.markdown(latest.read_text(encoding="utf-8"))

elif page == "Search":
    st.subheader("Search — hybrid retrieval + RAG answer")
    st.caption("BM25 + local semantic embeddings, fused (RRF) and cross-encoder reranked. "
               "Answer generated by your chosen provider; perplexity (confidence) is OpenAI-only.")

    with st.sidebar:
        st.divider()
        st.markdown("**Search settings**")
        use_semantic = st.checkbox("Semantic (embeddings)", value=True)
        use_rerank = st.checkbox("Cross-encoder rerank", value=True)
        top_k = st.slider("Passages (top-k)", 3, 15, 8)
        st.markdown("**Answer provider**")
        provider = st.selectbox("Provider", ["anthropic", "openai"])
        default_model = "claude-opus-4-8" if provider == "anthropic" else "gpt-4o"
        model = st.text_input("Model", value=default_model)
        env_key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        api_key = st.text_input(f"API key (or set ${env_key})", type="password")

    query = st.text_input("Query", placeholder="big-o cost of a linked list?")
    do_answer = st.checkbox("Generate an answer (RAG)", value=True)

    if st.button("Search", type="primary", disabled=not query.strip()):
        try:
            index = get_search_index(_wiki_signature(), use_semantic, use_rerank)
        except ModuleNotFoundError as e:
            st.error(f"Missing dependency: {e}. Run `pip install -r app/requirements.txt`.")
            st.stop()
        st.caption("Active modes: " + ", ".join(index.modes))
        hits = index.search(query.strip(), k=top_k)
        if not hits:
            st.info("No matches. Ingest some sources first.")
        else:
            if do_answer:
                from rag import llm, rag
                cfg = llm.LLMConfig(provider=provider, model=model, api_key=api_key or None)
                with st.spinner(f"Answering with {provider}…"):
                    try:
                        res = rag.answer(query.strip(), hits, cfg)
                    except ModuleNotFoundError as e:
                        st.error(f"Provider SDK not installed: {e}. `pip install {provider}`.")
                        st.stop()
                    except Exception as e:  # auth / network / model errors
                        st.error(f"Generation failed: {e}")
                        st.stop()
                st.markdown(res.answer)
                if res.perplexity is not None:
                    st.metric("Perplexity (lower = more confident)", f"{res.perplexity:.2f}")
                elif res.note:
                    st.caption(f"ℹ️ {res.note}")
                st.divider()
            st.markdown("**Retrieved passages**")
            for i, h in enumerate(hits, 1):
                with st.expander(f"[{i}] {h.chunk.rel_path} · {h.chunk.heading}  (score {h.score:.3f})"):
                    st.code(h.chunk.text)

elif page == "Browse wiki":
    st.subheader("Wiki browser")
    pages = wiki_pages()
    if not pages:
        st.info("Wiki is empty. Ingest a source first.")
    else:
        labels = {str(p.relative_to(VAULT)): p for p in pages}
        choice = st.selectbox("Page", list(labels))
        st.markdown(labels[choice].read_text(encoding="utf-8"))

elif page == "Status":
    st.subheader("Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Wiki pages", len(wiki_pages()))
    c2.metric("Saved answers", len(list(OUTPUT.glob("*.md"))) if OUTPUT.exists() else 0)
    inbox_lines = 0
    if RAW_INBOX.exists():
        inbox_lines = sum(1 for ln in RAW_INBOX.read_text(encoding="utf-8").splitlines()
                          if ln.strip() and not ln.startswith("#"))
    c3.metric("Inbox items", inbox_lines)
    b1, b2 = st.columns(2)
    if b1.button("Run lint"):
        with st.spinner("Health-checking the wiki…"):
            code, out = run_claude("/lint")
        st.code(out or "(no output)")
    if b2.button("Run gaps (study plan)"):
        with st.spinner("Finding learning gaps…"):
            code, out = run_claude("/gaps")
        st.code(out or "(no output)")
    st.divider()
    st.caption("Recent log (wiki/log.md)")
    if LOG.exists():
        st.code("\n".join(LOG.read_text(encoding="utf-8").splitlines()[-25:]))
