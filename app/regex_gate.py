import re

# Placeholder regex-based signal parser. In a full implementation this would
# contain the extraction logic for signals from raw Telegram messages.

SYMBOL_RE = re.compile(r"[A-Z]{2,10}")


def extract_symbol(text: str) -> str | None:
  m = SYMBOL_RE.search(text)
  return m.group(0) if m else None
