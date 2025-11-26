import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from spiral.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "config_loaded" in data
    assert "uptime_seconds" in data

def test_analyze_text():
    payload = {"text": "Test text", "mode": "BALANCED"}
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert "confidence" in data
    assert "success" in data
    assert "iterations" in data
    assert "pipeline_mode" in data
    assert "processing_time_ms" in data
    assert "timestamp" in data

def test_analyze_batch():
    payload = {"items": [
        {"text": "Test 1", "mode": "BALANCED"},
        {"text": "Test 2", "mode": "CREATIVE"}
    ]}
    response = client.post("/analyze/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "summary" in data
    assert len(data["results"]) == 2
    assert "average_confidence" in data["summary"]
    assert "average_success" in data["summary"]
    assert "total_iterations" in data["summary"]
    assert "total_processing_time_ms" in data["summary"]
