# rag/llm.py
from langchain_openai import ChatOpenAI

import config


class LLMProvider:
    def __init__(self):
        self._client = ChatOpenAI(
            model=config.LLM_MODEL,
            base_url=config.BASE_URL,
            api_key=config.API_KEY,
            temperature=0,
        )

    @property
    def client(self):
        return self._client
