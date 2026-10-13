"""Self-contained synthetic analytics demo. Never connects to an employer database."""
from datetime import date, timedelta
from pathlib import Path
import csv
import io
import random
import re
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DB = ROOT / "demo.sqlite3"
app = FastAPI(title="InsightFlow Analytics Demo", version="0.1.0")


def seed_database(path=DB):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, day TEXT, location TEXT, category TEXT, customer_id INTEGER, amount REAL, state TEXT)")
        if conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]:
            return
        rng = random.Random(42)
        today = date.today()
        rows = []
        for _ in range(1500):
            day = today - timedelta(days=rng.randrange(180))
            state = rng.choices(["completed", "cancelled"], [0.91, 0.09])[0]
            amount = round(rng.uniform(12, 145), 2) if state == "completed" else 0
            rows.append((day.isoformat(), rng.choice(["Central", "Riverside", "North"]), rng.choice(["Food", "Drinks", "Grocery"]), rng.randint(1, 370), amount, state))
        conn.executemany("INSERT INTO sales(day,location,category,customer_id,amount,state) VALUES (?,?,?,?,?,?)", rows)


def connect():
    if not DB.exists():
        seed_database()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# All SQL is fixed in code. No SQL or table identifiers arrive from users.
QUERIES = {
    "revenue": ("Monthly revenue", "SELECT substr(day,1,7) AS period, ROUND(SUM(amount),2) AS revenue FROM sales WHERE state='completed' GROUP BY period ORDER BY period"),
    "locations": ("Revenue by location", "SELECT location, ROUND(SUM(amount),2) AS revenue FROM sales WHERE state='completed' GROUP BY location ORDER BY revenue DESC"),
    "orders": ("Monthly order volume", "SELECT substr(day,1,7) AS period, COUNT(*) AS orders FROM sales GROUP BY period ORDER BY period"),
    "cancellations": ("Cancellation rate by location", "SELECT location, COUNT(*) AS orders, ROUND(100.0*SUM(CASE WHEN state='cancelled' THEN 1 ELSE 0 END)/COUNT(*),1) AS cancellation_rate FROM sales GROUP BY location ORDER BY cancellation_rate DESC"),
    "customers": ("Purchasing customers by location", "SELECT location, COUNT(DISTINCT customer_id) AS customers FROM sales WHERE state='completed' GROUP BY location ORDER BY customers DESC"),
    "categories": ("Revenue by category", "SELECT category, ROUND(SUM(amount),2) AS revenue FROM sales WHERE state='completed' GROUP BY category ORDER BY revenue DESC"),
    "aov": ("Average completed order value by location", "SELECT location, ROUND(AVG(amount),2) AS avg_order_value FROM sales WHERE state='completed' GROUP BY location ORDER BY avg_order_value DESC")
}
EXAMPLES = {
    "revenue": "Show monthly revenue",
    "locations": "Compare revenue by location",
    "orders": "How many orders per month?",
    "cancellations": "What is the cancellation rate by location?",
    "customers": "How many unique customers by location?",
    "categories": "Revenue breakdown by category",
    "aov": "Average order value by location"
}


def intent(question):
    q = question.lower()
    if re.search(r"\b(select|insert|update|delete|drop|alter|truncate|create|pragma|attach|detach|union)\b", q):
        return None
    if "average order" in q or "avg order" in q or "aov" in q:
        return "aov"
    if "category" in q or "categories" in q:
        return "categories"
    if any(w in q for w in ["cancel", "отмен"]):
        return "cancellations"
    if any(w in q for w in ["customer", "client", "клиент"]):
        return "customers"
    if any(w in q for w in ["order", "заказ"]):
        return "orders"
    if any(w in q for w in ["location", "branch", "restaurant"]):
        return "locations"
    if any(w in q for w in ["revenue", "sales", "выруч", "доход"]):
        return "revenue"
    return None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    return {"status": "ok", "dataset": "synthetic", "records": count}


@app.get("/api/examples")
def examples():
    return [{"id": k, "question": v} for k, v in EXAMPLES.items()]


@app.get("/api/kpis")
def kpis():
    with connect() as conn:
        row = conn.execute("SELECT ROUND(SUM(amount),2) AS revenue, COUNT(*) AS orders, COUNT(DISTINCT customer_id) AS customers, SUM(CASE WHEN state='cancelled' THEN 1 ELSE 0 END) AS cancellations FROM sales").fetchone()
        locations = conn.execute("SELECT COUNT(DISTINCT location) FROM sales").fetchone()[0]
    return {**dict(row), "locations": locations, "synthetic": True}


def insight(kind: str, rows: list[dict]) -> str:
    """Explain simple factual patterns, without an LLM or invented causality."""
    if not rows:
        return "No observations in the synthetic dataset."
    if kind == "revenue":
        first, last = rows[0], rows[-1]
        if len(rows) == 1:
            return f"Only one calendar month is represented: {last['period']}."
        delta = round(last["revenue"] - first["revenue"], 2)
        return (f"Revenue in {last['period']} is {last['revenue']:,.2f} USD "
                f"versus {first['revenue']:,.2f} USD in {first['period']} "
                f"(difference {delta:+,.2f} USD). Note: edge months may be partial.")
    if kind == "orders":
        top = max(rows, key=lambda x: x["orders"])
        return f"Highest recorded monthly order count: {top['period']} ({top['orders']:,} orders). Edge months may be partial."
    if kind == "cancellations":
        top = max(rows, key=lambda x: x["cancellation_rate"])
        return f"Highest cancellation rate: {top['location']} at {top['cancellation_rate']:.1f}% of recorded orders."
    metric = {"locations": "revenue", "categories": "revenue", "customers": "customers", "aov": "avg_order_value"}.get(kind)
    if not metric:
        return "Synthetic data summary."
    top = max(rows, key=lambda x: x[metric])
    label = top.get("location", top.get("category", "Unknown"))
    return f"Highest {metric.replace('_', ' ')}: {label} ({top[metric]:,.2f}). This is descriptive, not a causal finding."


@app.post("/api/chat")
def chat(request: ChatRequest):
    chosen = intent(request.question)
    if not chosen:
        return {"answer": "This demo supports revenue, orders, customers, cancellations and locations. Try an example.", "data": [], "columns": [], "supported": False}
    title, sql = QUERIES[chosen]
    with connect() as conn:
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
    return {"answer": f"{title}. {insight(chosen, rows)} Synthetic dataset; {len(rows)} rows.", "data": rows, "columns": list(rows[0]) if rows else [], "supported": True, "query_type": chosen}


@app.get("/api/export/{query_type}")
def export(query_type: str):
    if query_type not in QUERIES:
        raise HTTPException(status_code=404, detail="Unsupported report")
    with connect() as conn:
        rows = [dict(r) for r in conn.execute(QUERIES[query_type][1]).fetchall()]
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="demo_{query_type}.csv"'})
