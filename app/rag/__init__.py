"""RAG layer for the second brain: hybrid search + multi-provider LLM answering.

Optional layer (Karpathy's LLM Wiki is deliberately no-RAG). Used by the Streamlit
'Search' page to retrieve from wiki/ and answer with OpenAI or Anthropic.
All heavy deps (torch/sentence-transformers/openai/anthropic) are imported lazily
so the rest of the app runs without them installed.
"""
