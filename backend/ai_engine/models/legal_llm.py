"""
Legal LLM Service (Claude API Integration)
------------------------------------------
Generative AI for conversational legal answers using Anthropic's Claude.
Falls back to a structured knowledge-base response if the API key is absent
or the API is unreachable, so the Legal Assistant always returns useful info.
"""

import os
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

_client: anthropic.Anthropic | None = None

_SYSTEM_PROMPT = (
    "You are an expert AI Legal Assistant for the Kerala Police. "
    "Answer legal questions accurately based ONLY on the provided context from the knowledge base. "
    "Do not invent or guess legal information. If the context does not contain the answer, "
    "politely say so and suggest the officer consult a senior legal officer. "
    "Keep responses concise, professional, and relevant to Indian law (IPC/BNS/BNSS)."
)

_CONTEXT_SKIP_PREFIXES = ("FIR Narrative Context:",)


def _get_client() -> "anthropic.Anthropic | None":
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def warmup():
    """Check API key availability on startup."""
    print(f"[Legal LLM] Initializing Claude API integration... Model: {CLAUDE_MODEL}")
    if ANTHROPIC_API_KEY:
        print(f"[Legal LLM] ANTHROPIC_API_KEY found. Generative answers enabled via {CLAUDE_MODEL}.")
    else:
        print("[Legal LLM] ANTHROPIC_API_KEY not set. Legal Assistant will use knowledge-base fallback.")
        print("[Legal LLM] Add ANTHROPIC_API_KEY=sk-ant-... to your .env file to enable AI answers.")


def is_ready() -> bool:
    """Return True if the Claude API key is configured."""
    return bool(ANTHROPIC_API_KEY)


def generate_answer(question: str, context: str) -> str:
    """
    Generate a conversational legal answer using Claude.
    Falls back to a structured knowledge-base summary if the API is unavailable.
    """
    client = _get_client()
    if client is None:
        return _fallback_answer(question, context)

    user_message = f"Context from Legal Knowledge Base:\n{context}\n\nOfficer's Question:\n{question}"

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=[{
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    except anthropic.AuthenticationError:
        print("[Legal LLM] Invalid ANTHROPIC_API_KEY.")
        return _fallback_answer(question, context)

    except anthropic.RateLimitError:
        return (
            "The AI Legal Assistant is currently rate-limited. "
            "Here is the relevant information from the knowledge base:\n\n"
            + _format_context_as_answer(context)
        )

    except anthropic.APIConnectionError:
        return (
            "Cannot reach the Claude API. Check your internet connection.\n\n"
            + _format_context_as_answer(context)
        )

    except Exception as e:
        print(f"[Legal LLM] Generation error: {e}")
        return _fallback_answer(question, context)


def _fallback_answer(question: str, context: str) -> str:
    """
    Return a structured answer from the knowledge-base context when
    the Claude API is unavailable.
    """
    if not context or context == "No specific legal sections found for this query.":
        return (
            "I couldn't find specific legal sections for your query in the knowledge base. "
            "Try searching for a specific IPC/BNS section number (e.g. 'IPC 302') or "
            "a crime type (e.g. 'theft', 'assault').\n\n"
            "**Tip:** Set ANTHROPIC_API_KEY in your .env file for full conversational answers."
        )

    answer = _format_context_as_answer(context)
    answer += (
        "\n\n---\n"
        "*This answer is from the built-in legal knowledge base. "
        "Configure ANTHROPIC_API_KEY for AI-powered conversational answers.*"
    )
    return answer


def _format_context_as_answer(context: str) -> str:
    """Format raw context string into a readable answer."""
    lines = context.strip().split("\n")
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            formatted.append("")
        elif any(line.startswith(p) for p in _CONTEXT_SKIP_PREFIXES):
            continue
        else:
            formatted.append(line)

    return "\n".join(formatted).strip()
