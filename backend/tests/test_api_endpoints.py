import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_analytics_telemetry_endpoint():
    response = client.get("/api/v1/analytics/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "system_status" in data
    assert "indexes" in data

def test_analytics_benchmark_endpoint():
    response = client.get("/api/v1/analytics/eval-benchmark")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "fine_tuned_hybrid_reranker" in data["metrics"]

def test_documents_list_endpoint():
    response = client.get("/api/v1/documents/list")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
