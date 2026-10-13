# InsightFlow — Analytics Assistant Demo

Standalone portfolio analytics web application using **FastAPI, SQLite, HTML/JavaScript**, and a completely synthetic dataset. No employer database structure, credentials, private queries, logos or data.

## Features

- KPI overview across 1,500 synthetic retail orders, three fictional locations
- English-language analytics questions for monthly revenue, orders, customers, cancellations, and location revenue
- Safe predefined read-only SQL: user text is **never** executed as SQL
- Result tables, in-browser charts and CSV export
- REST API with interactive docs at `/docs`
- Automated API tests using pytest and GitHub Actions

**Not a production AI model.** Natural-language intent detection currently uses keyword routing; OpenAI integration is intentionally excluded from this first offline demo.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. Synthetic data is seeded automatically in a local SQLite file. To reset the demo, delete `demo.sqlite3` while the app is stopped.

## Test

```bash
pytest -q
```

## API

- `GET /api/kpis` — overview
- `GET /api/examples` — supported sample questions
- `POST /api/chat` — asks a supported question, returns structured data
- `GET /api/export/{query_type}` — CSV export

## Architecture

```text
Browser dashboard → FastAPI → strict intent routing → predefined SELECT queries
                                         ↘ synthetic SQLite retail dataset
```

Built from scratch as a **safe public portfolio reconstruction**, not a copy of proprietary company code.
