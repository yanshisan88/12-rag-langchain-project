from langchain_core.language_models import BaseLanguageModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from config import setting


def get_llm() -> BaseLanguageModel:

    provider = setting.LLM_PROVIDER

    if provider == "deepseek":
        return ChatDeepSeek(
            model=setting.DEEPSEEK_MODEL,
            api_key=setting.DEEPSEEK_API_KEY,
            base_url=setting.DEEPSEEK_BASE_URL
        ) 
    elif provider == "openai":
        return ChatOpenAI(
            model=setting.OPENAI_MODEL,
            api_key=setting.OPENAI_API_KEY,
            base_url=setting.OPENAI_BASE_URL,
            temperature=0.5,
            max_retries=3,
        )

    return ChatOllama(
        model=setting.OLLAMA_MODEL,
        base_url=setting.OLLAMA_BASE_URL,
    )

    

