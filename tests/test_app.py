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
