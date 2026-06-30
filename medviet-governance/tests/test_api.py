# tests/test_api.py
import sys
sys.modules["torch"] = None
import os
os.environ["PRESIDIO_DEVICE"] = "cpu"

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "MedViet Data API"}

# Admin (alice) can do everything
def test_admin_access():
    headers = {"Authorization": "Bearer token-alice"}
    
    # Read raw
    r = client.get("/api/patients/raw", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) <= 10

    # Read anonymized
    r = client.get("/api/patients/anonymized", headers=headers)
    assert r.status_code == 200

    # Read metrics
    r = client.get("/api/metrics/aggregated", headers=headers)
    assert r.status_code == 200

    # Delete
    r = client.delete("/api/patients/123", headers=headers)
    assert r.status_code == 200
    assert "deleted successfully" in r.json()["message"]

# ML Engineer (bob) cannot read raw or delete
def test_ml_engineer_access():
    headers = {"Authorization": "Bearer token-bob"}
    
    # Read raw -> 403
    r = client.get("/api/patients/raw", headers=headers)
    assert r.status_code == 403

    # Read anonymized -> 200
    r = client.get("/api/patients/anonymized", headers=headers)
    assert r.status_code == 200

    # Read metrics -> 200
    r = client.get("/api/metrics/aggregated", headers=headers)
    assert r.status_code == 200

    # Delete -> 403
    r = client.delete("/api/patients/123", headers=headers)
    assert r.status_code == 403

# Data Analyst (carol) can only read aggregated metrics
def test_data_analyst_access():
    headers = {"Authorization": "Bearer token-carol"}
    
    # Read raw -> 403
    r = client.get("/api/patients/raw", headers=headers)
    assert r.status_code == 403

    # Read anonymized -> 403
    r = client.get("/api/patients/anonymized", headers=headers)
    assert r.status_code == 403

    # Read metrics -> 200
    r = client.get("/api/metrics/aggregated", headers=headers)
    assert r.status_code == 200

    # Delete -> 403
    r = client.delete("/api/patients/123", headers=headers)
    assert r.status_code == 403

# Intern (dave) cannot access production endpoints
def test_intern_access():
    headers = {"Authorization": "Bearer token-dave"}
    
    r = client.get("/api/patients/raw", headers=headers)
    assert r.status_code == 403

    r = client.get("/api/patients/anonymized", headers=headers)
    assert r.status_code == 403

    r = client.get("/api/metrics/aggregated", headers=headers)
    assert r.status_code == 403

    r = client.delete("/api/patients/123", headers=headers)
    assert r.status_code == 403

# Token missing/invalid -> 401
def test_unauthorized_access():
    r = client.get("/api/patients/raw")
    assert r.status_code == 401

    headers = {"Authorization": "Bearer invalid-token"}
    r = client.get("/api/patients/raw", headers=headers)
    assert r.status_code == 401
