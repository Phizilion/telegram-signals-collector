from __future__ import annotations
from typing import Any
from .llm import LLMClient


class Processor:
  def __init__(self, llm: LLMClient, concurrency: int = 1):
    self.llm = llm
    self.concurrency = concurrency

  async def start(self) -> None:
    # Startup logic for the processor
    pass

  async def stop(self) -> None:
    # Shutdown logic for the processor
    pass

  async def process(self, message: Any) -> None:
    # Placeholder for processing an incoming message
    await self.llm.parse(str(message))
