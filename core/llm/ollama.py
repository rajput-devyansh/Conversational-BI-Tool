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