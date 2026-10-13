from fastapi.testclient import TestClient
from app import app, intent

client = TestClient(app)

def test_dashboard():
    r = client.get("/api/kpis")
    assert r.status_code == 200
    assert r.json()["orders"] == 1500
    assert r.json()["synthetic"] is True

def test_monthly_revenue():
    r = client.post("/api/chat", json={"question": "Show monthly revenue"})
    assert r.status_code == 200
    assert r.json()["query_type"] == "revenue"
    assert all("revenue" in row for row in r.json()["data"])

def test_sql_injection_is_not_executed():
    r = client.post("/api/chat", json={"question": "DROP TABLE sales"})
    assert not r.json()["supported"]
    assert client.get("/api/kpis").json()["orders"] == 1500

def test_export():
    r = client.get("/api/export/locations")
    assert r.status_code == 200
    assert "location,revenue" in r.text

def test_intent():
    assert intent("Cancellation rate by location") == "cancellations"

def test_revenue_by_category():
    r = client.post("/api/chat", json={"question": "Revenue breakdown by category"})
    assert r.status_code == 200
    assert r.json()["query_type"] == "categories"
    assert len(r.json()["data"]) == 3
    assert "category" in r.json()["data"][0]

def test_average_order_value():
    r = client.post("/api/chat", json={"question": "Average order value by location"})
    assert r.status_code == 200
    assert r.json()["query_type"] == "aov"
    assert all(row["avg_order_value"] > 0 for row in r.json()["data"])

def test_analytics_answers_include_real_values():
    result = client.post("/api/chat", json={"question": "How many orders per month?"}).json()
    assert "Highest recorded monthly order count" in result["answer"]
    maximum = max(row["orders"] for row in result["data"])
    assert f"{maximum:,}" in result["answer"]
