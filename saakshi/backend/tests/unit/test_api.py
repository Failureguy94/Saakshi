"""Unit tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base, get_db
from app.main import app

# In-memory SQLite for testing with StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["offline_mode"] is True
    assert "Saakshi" in data["app"]


def test_cases_crud_lifecycle() -> None:
    # 1. Create a case
    payload = {
        "case_number": "FIR-404/2026/CYBER",
        "title": "Suspected Jewelry Store DVR Tampering",
        "description": "Seized 4-channel Dahua DVR after reported burglary.",
        "investigator_name": "Insp. Vikram Singh",
        "agency": "Special Cell, Forensic Unit",
    }
    create_res = client.post("/cases", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["case_number"] == payload["case_number"]
    assert created["investigator_name"] == payload["investigator_name"]
    case_id = created["id"]

    # 2. Get the created case
    get_res = client.get(f"/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == case_id

    # 3. List cases
    list_res = client.get("/cases")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1
    assert any(c["id"] == case_id for c in items)

    # 4. Duplicate case number should return 409 Conflict
    dup_res = client.post("/cases", json=payload)
    assert dup_res.status_code == 409


def test_nonexistent_case_returns_404() -> None:
    res = client.get("/cases/nonexistent-case-id-123")
    assert res.status_code == 404
