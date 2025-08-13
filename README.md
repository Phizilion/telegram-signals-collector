# Telegram Signal Collector

Collect **new** trading signals from Telegram channels you’re subscribed to. Uses **Pyrogram** to receive channel messages, **LangChain + OpenAI** to classify/parse, and **SQLAlchemy** to persist to **SQLite**.  
Pipeline is **simple and direct**: each message is processed inline — **no queues**, **no rate limits**.

## Highlights
- No history scraping; only **new messages** as they arrive.
- LLM **classification** + **structured parsing** (Pydantic model).
- Minimal valid signal: `symbol`, `side`, `take_profits`.
- JSON arrays for `take_profits` / `stop_loss`.
- API endpoints (FastAPI) + lightweight React viewer.

---

## First-time Telegram login
1. Fill `.env` (see `.env.example`) with `API_ID` and `API_HASH`.
2. Run:
   ```bash
   python -m app.login
   ```
   Follow the interactive login. A session file is created at `${TELEGRAM_SESSION_DIR}/${TELEGRAM_SESSION_NAME}.session`.

## Running (API + Collector)
Use Python 3.13.

```bash
python -m venv .venv
source .venv/bin/activate
poetry install  # or: pip install -r requirements.txt if you keep one
uvicorn app.api.server:app --reload
```

- On startup, the app initializes the DB, builds the LLM client, starts the Telegram listener, and immediately begins processing new channel messages inline.

## Running the Viewer (optional)
```bash
cd web
npm i
npm run dev
```
The dev server proxies `/api` to `http://localhost:8000`.

## Environment
See `.env.example`. Key values:
- **Telegram**: `API_ID`, `API_HASH`, `TELEGRAM_SESSION_DIR`, `TELEGRAM_SESSION_NAME`
- **LLM**: `OPENAI_API_KEY`, `OPENAI_MODEL` (default: `gpt-4o-mini`)
- **DB**: `DB_URL` (default: `sqlite+aiosqlite:///./signals.db`)

## Database
- Default SQLite DB: `signals.db`
- Tables: `channels`, `signals`
- Uniqueness: `(channel_id, message_id)` prevents duplicates
- UTC times

## API (selected)
- `GET /api/health`
- `GET /api/channels`
- `GET /api/symbols`
- `GET /api/channels/{channel_id}/signals?limit&offset`
- `GET /api/symbols/{symbol}/signals?limit&offset`
- `GET /api/stats/channels`
- `GET /api/stats/symbols`

## Notes / Extending
- A small regex **gate** quickly filters obvious noise; LLM still makes final decision + structured parse.
- Handle message edits by wiring Pyrogram’s edit handler and updating by `(channel_id, message_id)`.
- Swap `ChatOpenAI` for another `BaseLanguageModel` if needed.

> Design choice: We intentionally removed the async queue and any concurrency semaphores. Processing is inline per-message for simplicity and lower latency. If you later need throttling/backpressure, reintroduce a queue/sem at the integration boundary.
