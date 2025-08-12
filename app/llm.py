from __future__ import annotations
import asyncio
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .schemas import SignalFields
from .config import settings


# System prompts kept tight and deterministic.
_SIGNAL_CLASSIFIER_SYSTEM = (
  "You are a precise classifier. Decide if the user message contains a concrete trading signal "
  "with explicit intent to open a position (long/short or buy/sell) and at least one target (TP). "
  "Return only 'yes' or 'no'."
)

_SIGNAL_PARSER_SYSTEM = (
  "You are a strict information extractor. From the message, extract a single trading signal. "
  "Rules: symbol must be the base asset without USDT suffix; side is long/short; leverage integer if present; "
  "stop_loss can be one or multiple numbers; take_profits must be one or more numbers. "
  "If information is absent, leave it null. Do not guess."
)


class LLMClient:
  """Wraps LangChain LLMs for classification and structured parsing."""

  def __init__(self) -> None:
    self.llm = ChatOpenAI(
      model=settings.openai_model,
      api_key=settings.openai_api_key,  # <-- pass explicitly
      temperature=0,
      max_tokens=400,
      timeout=30,
    )
    self._sem = asyncio.Semaphore(settings.parser_concurrency)

    # Build prompts
    self._cls_prompt = ChatPromptTemplate.from_messages([
      ("system", _SIGNAL_CLASSIFIER_SYSTEM),
      ("human", "Message: {message} Answer 'yes' or 'no' only."),
    ])

    self._parse_prompt = ChatPromptTemplate.from_messages([
      ("system", _SIGNAL_PARSER_SYSTEM),
      ("human", "Message to parse:{message}"),
    ])

    # Structured output for parsing
    self._structured_llm = self.llm.with_structured_output(SignalFields)

  async def is_signal(self, text: str) -> bool:
    prompt = self._cls_prompt.format_messages(message=text)
    async with self._sem:
      resp = await self.llm.ainvoke(prompt)
    content = (resp.content or "").strip().lower()
    return content.startswith("y")  # yes/no only

  async def parse_signal(self, text: str) -> Optional[SignalFields]:
    prompt = self._parse_prompt.format_messages(message=text)
    async with self._sem:
      try:
        result: SignalFields = await self._structured_llm.ainvoke(prompt)
        if not result.symbol or not result.take_profits or not result.side:
          return None
        return result
      except Exception:
        return None