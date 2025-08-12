# Telegram Signal Collector

Collects **real-time** trading signals from Telegram channels you are subscribed to. Uses **Pyrogram** to receive new channel messages, **LangChain + OpenAI** to detect/parse signals, and **SQLAlchemy** to store into **SQLite**.

## Features
- No history scraping; only **new messages**.
- LLM **classification** + **structured parsing** (Pydantic model).
- Minimal valid signal: `symbol`, `side`, `take_profits`.
- Robust async pipeline with backpressure, dedup, and graceful error handling.

### First-time Telegram login

1) Set `API_ID` and `API_HASH` in `.env`.
2) (Optional) Set `TELEGRAM_PHONE` (and `TELEGRAM_PASSWORD` if 2FA) to avoid some prompts.
3) Run:

```bash
python -m app.login
```

## Setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Fill `.env` from `.env.example`.
   - Create a Pyrogram session string (login once) and set `SESSION_STRING`.
   - Set `OPENAI_API_KEY` and `OPENAI_MODEL` (default `gpt-4o-mini`).
4. Run: `python -m app.main`

## Database
- SQLite file: `signals.db` (by default).
- Tables: `channels`, `signals`.
- `signals.take_profits` and `signals.stop_loss` are stored as JSON arrays.

## Notes
- Heuristic gate reduces LLM calls; final parsing still uses LLM.
- If a message is reposted/duplicate, `(channel_id, message_id)` unique constraint prevents double inserts.
- Time is stored in UTC.

## Extending
- Add retries around LLM calls if needed.
- Handle message edits by listening to `on_edited_message` and updating records.
- Add additional providers by swapping `ChatOpenAI` for another LangChain `BaseLanguageModel`.