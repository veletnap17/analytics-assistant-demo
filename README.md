# InsightFlow — Analytics Assistant Demo

**Live demo:** https://analytics-assistant-demo.onrender.com

A portfolio proof of concept for conversational business analytics: explore synthetic retail KPIs, choose a predefined report, visualize results, and export CSV.

**Tech stack:** Python · FastAPI · SQL · SQLite · HTML/CSS/JavaScript · Docker · GitHub Actions · Render

> **Portfolio scope:** Uses 1,500 synthetic orders across three fictional locations. Keyword-based intent routing and predefined read-only queries — not a generative AI model. No employer code or customer data.

Standalone portfolio analytics web application using **FastAPI, SQLite, HTML/JavaScript**, and a completely synthetic dataset. No employer database structure, credentials, private queries, logos or data.

## What to try

1. Open the **[live application](https://analytics-assistant-demo.onrender.com)** (free hosting may take ~1 minute to wake up).
2. Select **What is the cancellation rate by location?** to see a labeled percentage chart.
3. Switch **Chart / Table**, then try **Revenue breakdown by category**.
4. Use **Export CSV** to download the displayed report.

## Features

- KPI overview across 1,500 synthetic retail orders, three fictional locations
- English-language analytics questions for monthly revenue, orders, customers, cancellations, revenue by location/category, and average order value
- Data-grounded descriptive insights: highlights, comparisons and caveats derived from query rows, without inventing causes
- Safe predefined read-only SQL: user text is **never** executed as SQL
- Result tables, in-browser charts with chart/table switcher and CSV export
- Recent successful questions saved in your browser (localStorage), with a clear-history action; no chat history sent to a server
- REST API with interactive docs at `/docs`
- Automated API tests using pytest and GitHub Actions

**Not a production AI model.** Natural-language intent detection currently uses keyword routing; OpenAI integration is intentionally excluded from this first offline demo.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:8000. The script binds to localhost only; this is a local development entry point.

Alternatively, run with Docker:

```bash
docker build -t insightflow-demo .
docker run --rm -p 127.0.0.1:8000:8000 insightflow-demo
```

The container uses an ephemeral SQLite database, recreated on a fresh container run. Synthetic data is seeded automatically in a local SQLite file. To reset the demo, delete `demo.sqlite3` while the app is stopped.

## Test

```bash
python -m pytest -q
```

## Security and limits

The demo uses entirely generated retail orders and fixed SQL templates; no internal database names, credentials, branded media, or employer integrations are included. Browser history stays in localStorage. User-submitted questions are classified into predefined report types; **it is not an AI model**.

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

### Interpreting the demo
Insights are generated deterministically from synthetic query results, not by an AI model. Month-to-month comparisons include potentially partial boundary months; they are illustrative and should not be used as business decisions.

## Hosting

The live demo is hosted on Render. A `render.yaml` file describes the optional deployment configuration and `/api/health` provides a health check. The free instance may spin down when idle. Publishing the website does not require making the source repository public.

