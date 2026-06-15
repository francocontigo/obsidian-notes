"""Provider abstraction: generate an answer with OpenAI or Anthropic.

Perplexity (a confidence metric = exp(mean negative token logprob)) is computed
ONLY for OpenAI, because Anthropic does not expose token logprobs. When the
provider can't give logprobs, `perplexity` is None and `note` explains why.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Sensible defaults. Anthropic default follows the claude-api guidance (Opus 4.8).
ANTHROPIC_DEFAULT = "claude-opus-4-8"
OPENAI_DEFAULT = "gpt-4o"


@dataclass
class LLMConfig:
    provider: str            # "openai" | "anthropic"
    model: str
    api_key: str | None = None


@dataclass
class GenerationResult:
    text: str
    perplexity: float | None   # None when the provider doesn't expose logprobs
    note: str | None = None


def generate(system: str, user: str, cfg: LLMConfig, max_tokens: int = 4096) -> GenerationResult:
    if cfg.provider == "anthropic":
        return _anthropic(system, user, cfg, max_tokens)
    if cfg.provider == "openai":
        return _openai(system, user, cfg, max_tokens)
    raise ValueError(f"Unknown provider: {cfg.provider!r}")


def _anthropic(system: str, user: str, cfg: LLMConfig, max_tokens: int) -> GenerationResult:
    import anthropic  # official SDK

    client = anthropic.Anthropic(api_key=cfg.api_key) if cfg.api_key else anthropic.Anthropic()
    resp = client.messages.create(
        model=cfg.model or ANTHROPIC_DEFAULT,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},   # recommended default for Opus 4.x
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    # content is a list of blocks; thinking blocks may precede the text block.
    text = "".join(b.text for b in resp.content if b.type == "text")
    return GenerationResult(
        text=text,
        perplexity=None,
        note="Anthropic não expõe logprobs — perplexidade indisponível neste provider.",
    )


def _openai(system: str, user: str, cfg: LLMConfig, max_tokens: int) -> GenerationResult:
    from openai import OpenAI  # official SDK

    client = OpenAI(api_key=cfg.api_key) if cfg.api_key else OpenAI()
    resp = client.chat.completions.create(
        model=cfg.model or OPENAI_DEFAULT,
        max_tokens=max_tokens,
        logprobs=True,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    choice = resp.choices[0]
    text = choice.message.content or ""
    return GenerationResult(text=text, perplexity=_perplexity(choice.logprobs))


def _perplexity(logprobs) -> float | None:
    """exp(-mean(token logprob)). Lower = the model was more confident."""
    content = getattr(logprobs, "content", None) if logprobs else None
    if not content:
        return None
    lps = [t.logprob for t in content if t.logprob is not None]
    if not lps:
        return None
    return math.exp(-sum(lps) / len(lps))
