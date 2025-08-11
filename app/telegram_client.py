from __future__ import annotations
from .processor import Processor


class TelegramListener:
  def __init__(self, processor: Processor):
    self.processor = processor

  async def start(self) -> None:
    # Start listening to Telegram (stub)
    pass

  async def stop(self) -> None:
    # Stop listening (stub)
    pass
