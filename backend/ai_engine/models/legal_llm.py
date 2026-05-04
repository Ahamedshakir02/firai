"""
Legal LLM Service (Ollama Integration)
--------------------------------------
Local generative AI for conversational legal answers.
Connects to an Ollama instance running on the host machine.
100% offline and sovereign.
"""

import os
import httpx

# host.docker.internal resolves to the Windows host machine from inside the Docker container
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

def warmup():
    """
    Check if Ollama is accessible on startup.
    Does not block if Ollama is not running yet.
    """
    print(f"[Legal LLM] Warming up Ollama integration... Target: {OLLAMA_URL}, Model: {OLLAMA_MODEL}")
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                print(f"[Legal LLM] Connected to Ollama. Available models: {', '.join(models)}")
                
                # Check if requested model exists
                if not any(OLLAMA_MODEL in m for m in models):
                    print(f"[Legal LLM] WARNING: Model '{OLLAMA_MODEL}' not found. You may need to run `ollama pull {OLLAMA_MODEL}` on your host machine.")
            else:
                print(f"[Legal LLM] Ollama is responding but returned status {response.status_code}")
    except Exception as e:
        print(f"[Legal LLM] Ollama not accessible yet. Will retry on first query. Error: {e}")

def is_ready():
    # Ollama is an external service, we assume it's ready and handle failures during the request
    return True

def generate_answer(question: str, context: str) -> str:
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
                f"{OLLAMA_URL}/api/generate",
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
                print(f"[Legal LLM] Ollama API Error: {response.text}")
                return "I'm having trouble communicating with the local Ollama brain. Please ensure Ollama is running on your host machine."
                
    except httpx.ConnectError:
        return (
            "Cannot connect to the local AI engine. "
            f"Please ensure Ollama is running on your host machine and the model `{OLLAMA_MODEL}` is downloaded."
        )
    except httpx.ReadTimeout:
        return "The local AI engine is taking too long to respond. It might be overloaded or still loading the model into memory."
    except Exception as e:
        print(f"[Legal LLM] Generation error: {e}")
        return "I encountered an error while generating a response. Please check the backend logs."
