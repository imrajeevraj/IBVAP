from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.models.user import User

client = TestClient(app)
token = create_access_token("testadmin", "ADMIN")
client.headers = {"Authorization": f"Bearer {token}"}

def test_system_health_detailed(db_session):
    db_session.add(User(username="testadmin", hashed_password="x", role="ADMIN"))
    db_session.commit()

    response = client.get("/api/system/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "database_status" in data
    
    # We should have valid values
    assert 0 <= data["cpu"]["percent"] <= 100
    assert 0 <= data["memory"]["percent"] <= 100
    assert data["memory"]["used_mb"] >= 0
    assert data["memory"]["total_mb"] >= data["memory"]["used_mb"]
    assert 0 <= data["disk"]["percent"] <= 100

def test_system_health_quick(db_session):
    db_session.add(User(username="testadmin", hashed_password="x", role="ADMIN"))
    db_session.commit()

    response = client.get("/api/system/health/quick")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "is_healthy" in data
    assert isinstance(data["is_healthy"], bool)
