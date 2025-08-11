# Telegram Signal Collector

This project collects trading signals from Telegram channels, parses them and exposes
a FastAPI backend with a React frontend for browsing channels, symbols and signal
statistics.

## Backend

The backend lives under `app/` and exposes an API under `/api`. Run it with:

```bash
uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000
```

## Frontend

The web UI resides in `web/` and is built with React, Vite and Tailwind.

```bash
cd web
npm install
npm run dev
```

## Environment

Copy `.env.example` to `.env` and adjust as needed.
