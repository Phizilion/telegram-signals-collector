from __future__ import annotations
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas import SignalFields
from app.config import settings

# System prompts kept tight and deterministic.
_SIGNAL_CLASSIFIER_SYSTEM = (
    "You are a precise classifier. Decide if the user message contains a concrete trading signal "
    "with explicit intent or request to open a position (long/short or buy/sell). Be accurate. "
    "Return only `yes` or `no`."
)

_SIGNAL_PARSER_SYSTEM = (
    "You are a strict information extractor. From the message, extract a data of single trading signal. "
    "stop_loss can be one or multiple numbers; take_profits can be one or multiple numbers. "
    "If information is absent, leave it null. Do not guess."
)


class LLMClient:
    """LangChain LLMs for classification and structured parsing (no rate limiting)."""

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
            max_tokens=400,
            timeout=30,
        )

        self._cls_prompt = ChatPromptTemplate.from_messages(
            [("system", _SIGNAL_CLASSIFIER_SYSTEM), ("human", "Message to classify: `{message}`")]
        )
        self._parse_prompt = ChatPromptTemplate.from_messages(
            [("system", _SIGNAL_PARSER_SYSTEM), ("human", "Message to parse: `{message}`")]
        )

        self._structured_llm = self.llm.with_structured_output(SignalFields)

    async def is_signal(self, text: str) -> bool:
        prompt = self._cls_prompt.format_messages(message=text)
        resp = await self.llm.ainvoke(prompt)
        content = (resp.content or "").strip().lower()
        return content.startswith("y")  # yes/no only

    async def parse_signal(self, text: str) -> Optional[SignalFields]:
        prompt = self._parse_prompt.format_messages(message=text)
        try:
            result: SignalFields = await self._structured_llm.ainvoke(prompt)
            if not result.symbol or not result.take_profits or not result.side:
                return None
            return result
        except Exception:
            return None
