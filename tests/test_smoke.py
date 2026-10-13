"""Smoke tests for the browser entrypoint and predefined analysis routes."""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_frontend_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "InsightFlow" in response.text
    assert 'id="form"' in response.text

def test_examples_all_execute():
    examples = client.get("/api/examples").json()
    assert len(examples) >= 7
    for example in examples:
        response = client.post("/api/chat", json={"question": example["question"]})
        assert response.status_code == 200
        assert response.json()["supported"] is True, example["question"]
        assert response.json()["data"], example["question"]

def test_unknown_question_is_safe():
    response = client.post("/api/chat", json={"question": "Predict tomorrow's exchange rate"})
    assert response.status_code == 200
    assert response.json()["supported"] is False
