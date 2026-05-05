"""
Legal LLM Service (Ollama Integration)
--------------------------------------
Local generative AI for conversational legal answers.
Connects to an Ollama instance running on the host machine.
100% offline and sovereign.

Falls back to a structured knowledge-base response if Ollama
is unreachable, so the Legal Assistant remains functional even
without a running LLM.
"""

import os
import httpx

# Determine the best Ollama URL:
#   1. Explicit OLLAMA_URL env var (highest priority)
#   2. host.docker.internal (for Docker containers)
#   3. localhost (for local development)
_OLLAMA_URL_CANDIDATES = [
    os.environ.get("OLLAMA_URL", ""),
    "http://localhost:11434",
    "http://127.0.0.1:11434",
    "http://host.docker.internal:11434",
]

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# Resolved at warmup
_ollama_url = None
_detection_attempted = False


def _detect_ollama_url() -> str:
    """Try each candidate URL and return the first one that responds."""
    for url in _OLLAMA_URL_CANDIDATES:
        url = url.strip()
        if not url:
            continue
        try:
            # Use explicit connect timeout to prevent hanging on unreachable hosts
            timeout = httpx.Timeout(3.0, connect=1.5)
            with httpx.Client(timeout=timeout) as client:
                response = client.get(f"{url}/api/tags")
                if response.status_code == 200:
                    return url
        except Exception:
            continue
    return ""


def warmup():
    """
    Check if Ollama is accessible on startup.
    Does not block if Ollama is not running yet.
    """
    global _ollama_url, _detection_attempted
    print(f"[Legal LLM] Warming up Ollama integration... Model: {OLLAMA_MODEL}")
    
    _ollama_url = _detect_ollama_url()
    _detection_attempted = True
    
    if _ollama_url:
        try:
            timeout = httpx.Timeout(3.0, connect=1.5)
            with httpx.Client(timeout=timeout) as client:
                response = client.get(f"{_ollama_url}/api/tags")
                if response.status_code == 200:
                    models = [m["name"] for m in response.json().get("models", [])]
                    print(f"[Legal LLM] Connected to Ollama at {_ollama_url}. Available models: {', '.join(models)}")
                    
                    # Check if requested model exists
                    if not any(OLLAMA_MODEL in m for m in models):
                        print(f"[Legal LLM] WARNING: Model '{OLLAMA_MODEL}' not found. You may need to run `ollama pull {OLLAMA_MODEL}` on your host machine.")
        except Exception as e:
            print(f"[Legal LLM] Ollama detection succeeded but verification failed: {e}")
    else:
        print(f"[Legal LLM] Ollama not accessible on any candidate URL. Legal Assistant will use knowledge-base fallback.")
        print(f"[Legal LLM] To enable generative answers, start Ollama and ensure model '{OLLAMA_MODEL}' is pulled.")


def is_ready():
    """Check if Ollama is likely available."""
    return bool(_ollama_url)


def generate_answer(question: str, context: str) -> str:
    """
    Generate a conversational legal answer using Ollama.
    Falls back to a structured knowledge-base summary if Ollama is unavailable.
    """
    global _ollama_url, _detection_attempted
    
    # If no URL was found during warmup and we haven't retried yet, try once more
    if not _ollama_url and not _detection_attempted:
        _ollama_url = _detect_ollama_url()
        _detection_attempted = True
    
    # If still no URL, return a structured fallback from the context immediately
    if not _ollama_url:
        return _fallback_answer(question, context)
    
    system_prompt = (
        "You are an expert AI Legal Assistant for the Kerala Police. "
        "Your task is to answer legal questions accurately based ONLY on the provided context. "
        "Do not invent or guess any legal information. If the context does not contain the answer, "
        "politely inform the user. Keep your answer conversational, concise, and professional."
    )
    
    prompt = f"System:\n{system_prompt}\n\nContext from Knowledge Base:\n{context}\n\nUser Question:\n{question}"
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{_ollama_url}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response generated.")
            else:
                print(f"[Legal LLM] Ollama API Error ({response.status_code}): {response.text[:200]}")
                return _fallback_answer(question, context)
                
    except httpx.ConnectError:
        # Ollama went offline — clear the cached URL so we re-detect next time
        _ollama_url = None
        return _fallback_answer(question, context)
    except httpx.ReadTimeout:
        return (
            "⏳ The local AI engine is taking too long to respond. "
            "Here is the relevant information from the knowledge base:\n\n"
            + _format_context_as_answer(context)
        )
    except Exception as e:
        print(f"[Legal LLM] Generation error: {e}")
        return _fallback_answer(question, context)


def _fallback_answer(question: str, context: str) -> str:
    """
    Generate a structured answer from the knowledge-base context
    when Ollama is not available. This ensures the Legal Assistant
    always returns useful information.
    """
    if not context or context == "No specific legal sections found for this query.":
        return (
            "I couldn't find specific legal sections for your query in the knowledge base. "
            "Try searching for a specific IPC/BNS section number (e.g., 'IPC 302') or "
            "a crime type (e.g., 'theft', 'assault').\n\n"
            "💡 **Tip:** The generative AI (Ollama) is not currently running. "
            "Start Ollama with the `llama3.2` model for more detailed conversational answers."
        )
    
    answer = _format_context_as_answer(context)
    answer += (
        "\n\n---\n"
        "ℹ️ *This answer is based on the built-in legal knowledge base. "
        "For more detailed conversational analysis, ensure Ollama is running.*"
    )
    return answer


def _format_context_as_answer(context: str) -> str:
    """Format raw context string into a readable answer."""
    # The context is already well-formatted from firai_engine.py
    # Just clean it up slightly for direct display
    lines = context.strip().split("\n")
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            formatted.append("")
        elif line.startswith("FIR Narrative Context:"):
            continue  # Skip the raw narrative context header
        else:
            formatted.append(line)
    
    return "\n".join(formatted).strip()
