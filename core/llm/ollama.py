from langchain_ollama import ChatOllama
from core.llm.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
    OLLAMA_TIMEOUT
)

def get_ollama_llm(
    model: str = OLLAMA_MODEL,
    temperature: float = OLLAMA_TEMPERATURE,
):
    """
    Returns a LangChain-compatible Ollama Chat model.
    """

    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=model,
        temperature=temperature,
        timeout=OLLAMA_TIMEOUT
    )

def get_chart_llm():
    """
    Dedicated LLM for chart selection (Issue #13).
    Uses a small, instruction-following model.
    """
    return get_ollama_llm(
        model="phi4-mini:3.8b",
        temperature=0
    )