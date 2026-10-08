import os
os.environ["JWT_SECRET"] = "test-secret-with-at-least-thirty-two-characters"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.auth import hash_password
from app.db import get_db
from app.main import app
from app.models import Base, User

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([
            User(email="employee@example.test", role="employee", password_hash=hash_password("pass12345")),
            User(email="other@example.test", role="employee", password_hash=hash_password("pass12345")),
            User(email="it@example.test", role="agent", department="IT", password_hash=hash_password("pass12345")),
            User(email="hr@example.test", role="agent", department="HR", password_hash=hash_password("pass12345")),
            User(email="admin@example.test", role="admin", password_hash=hash_password("pass12345")),
        ])
        db.commit()
    def override_db():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()

def auth(client, email):
    response = client.post("/api/login", json={"email": email, "password": "pass12345"})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}

def test_employee_it_ticket_agent_updates_employee_sees_history(client):
    employee = auth(client, "employee@example.test")
    it = auth(client, "it@example.test")
    hr = auth(client, "hr@example.test")
    created = client.post("/api/tickets", headers=employee, json={"title": "Laptop broken", "description": "Screen is black", "impact": "Cannot work on the main laptop", "category": "IT"})
    assert created.status_code == 201
    ticket = created.json()
    assert ticket["department"] == "IT" and ticket["status"] == "Open"
    assert len(ticket["history"]) == 1
    ticket_id = ticket["id"]
    assert any(t["id"] == ticket_id for t in client.get("/api/tickets", headers=it).json())
    assert client.get("/api/tickets", headers=hr).json() == []
    assert client.patch(f"/api/tickets/{ticket_id}/status", headers=hr, json={"status": "In Progress"}).status_code == 404
    assert client.patch(f"/api/tickets/{ticket_id}/status", headers=it, json={"status": "Done"}).status_code == 409
    for status in ("In Progress", "Done"):
        response = client.patch(f"/api/tickets/{ticket_id}/status", headers=it, json={"status": status})
        assert response.status_code == 200
    result = client.get(f"/api/tickets/{ticket_id}", headers=employee).json()
    assert result["status"] == "Done"
    assert [h["to_status"] for h in result["history"]] == ["Open", "In Progress", "Done"]
    assert client.get("/api/dashboard", headers=employee).json() == {"total": 1, "by_department": {"IT": 1, "HR": 0, "FAC": 0, "FIN": 0, "PROC": 0}}

def test_category_validation_and_permissions(client):
    employee = auth(client, "employee@example.test")
    other = auth(client, "other@example.test")
    it = auth(client, "it@example.test")
    admin = auth(client, "admin@example.test")
    assert client.post("/api/tickets", headers=employee, json={"title": "Wrong queue", "description": "Should be rejected", "impact": "No impact", "category": "Finance"}).status_code == 422
    assert client.post("/api/tickets", headers=it, json={"title": "Agent ticket", "description": "Not allowed", "impact": "No impact", "category": "IT"}).status_code == 403
    created = client.post("/api/tickets", headers=employee, json={"title": "HR question", "description": "Leave policy", "impact": "Work continues while waiting for the answer", "category": "HR", "department": "IT"})
    assert created.status_code == 201
    ticket = created.json()
    assert ticket["department"] == "HR"
    assert ticket["priority"] == "Normal"
    assert created.json()["impact"] == "Work continues while waiting for the answer"
    assert client.post("/api/tickets", headers=employee, json={"title": "Urgent IT issue", "description": "Critical device failure", "impact": "Many staff cannot work", "category": "IT", "priority": "Urgent"}).status_code == 422
    assert client.post("/api/tickets", headers=employee, json={"title": "Bad priority", "description": "Invalid value", "impact": "No impact", "category": "IT", "priority": "Critical"}).status_code == 422
    assert client.get(f"/api/tickets/{ticket['id']}", headers=other).status_code == 404
    assert client.patch(f"/api/tickets/{ticket['id']}/status", headers=employee, json={"status": "In Progress"}).status_code == 403
    assert ticket["id"] in [item["id"] for item in client.get("/api/tickets", headers=admin).json()]
    assert client.get("/api/tickets").status_code == 401
    assert client.post("/api/login", json={"email": "employee@example.test", "password": "wrong"}).status_code == 401

def test_ticket_conversation_is_shared_only_with_ticket_participants(client):
    employee = auth(client, "employee@example.test")
    other = auth(client, "other@example.test")
    it = auth(client, "it@example.test")
    hr = auth(client, "hr@example.test")
    created = client.post("/api/tickets", headers=employee, json={
        "title": "VPN access", "description": "Cannot connect to VPN", "impact": "Remote work is blocked", "category": "IT"
    })
    ticket_id = created.json()["id"]

    first = client.post(f"/api/tickets/{ticket_id}/messages", headers=employee, json={"body": "  VPN fails after sign-in.  "})
    assert first.status_code == 201
    assert first.json()["body"] == "VPN fails after sign-in."
    assert first.json()["author_email"] == "employee@example.test"
    assert first.json()["author_role"] == "employee"
    second = client.post(f"/api/tickets/{ticket_id}/messages", headers=employee, json={"body": "I have tried twice."})
    assert second.status_code == 201
    assert client.get("/api/unread-counts", headers=it).json() == {str(ticket_id): 2}
    assert client.get("/api/unread-counts", headers=employee).json() == {}
    assert client.get("/api/unread-counts", headers=hr).json() == {}
    assert client.post(f"/api/tickets/{ticket_id}/messages/read", headers=other).status_code == 404

    reply = client.post(f"/api/tickets/{ticket_id}/messages", headers=it, json={"body": "Please try again; we reset your access."})
    assert reply.status_code == 201
    assert reply.json()["author_role"] == "agent"
    assert [m["id"] for m in client.get(f"/api/tickets/{ticket_id}/messages", headers=employee).json()] == [first.json()["id"], second.json()["id"], reply.json()["id"]]
    assert client.get("/api/unread-counts", headers=employee).json() == {str(ticket_id): 1}
    assert client.post(f"/api/tickets/{ticket_id}/messages/read", headers=it).json()["unread"] == 0
    assert client.get("/api/unread-counts", headers=it).json() == {}
    assert client.post(f"/api/tickets/{ticket_id}/messages/read", headers=employee).json()["unread"] == 0
    assert client.get("/api/unread-counts", headers=employee).json() == {}
    assert client.get(f"/api/tickets/{ticket_id}/messages", headers=it).status_code == 200
    assert client.get(f"/api/tickets/{ticket_id}/messages", headers=hr).status_code == 404
    assert client.get(f"/api/tickets/{ticket_id}/messages", headers=other).status_code == 404
    assert client.post(f"/api/tickets/{ticket_id}/messages", headers=other, json={"body": "Not allowed"}).status_code == 404
    assert client.post(f"/api/tickets/{ticket_id}/messages", headers=employee, json={"body": "   "}).status_code == 422

def test_only_responsible_agents_and_admins_can_set_priority(client):
    employee = auth(client, "employee@example.test")
    it = auth(client, "it@example.test")
    hr = auth(client, "hr@example.test")
    admin = auth(client, "admin@example.test")
    it_ticket = client.post("/api/tickets", headers=employee, json={
        "title": "Shared drive unavailable", "description": "Cannot open shared files",
        "impact": "Five people cannot access today's work files", "category": "IT",
    }).json()
    ticket_id = it_ticket["id"]
    assert it_ticket["priority"] == "Normal"
    assert it_ticket["priority_history"] == []
    assert client.patch(f"/api/tickets/{ticket_id}/priority", headers=employee, json={"priority": "Urgent"}).status_code == 403
    assert client.patch(f"/api/tickets/{ticket_id}/priority", headers=hr, json={"priority": "Urgent"}).status_code == 404

    escalated = client.patch(f"/api/tickets/{ticket_id}/priority", headers=it, json={"priority": "Urgent"})
    assert escalated.status_code == 200
    assert escalated.json()["priority"] == "Urgent"
    event = escalated.json()["priority_history"][0]
    assert (event["from_priority"], event["to_priority"], event["actor_email"]) == ("Normal", "Urgent", "it@example.test")
    assert client.patch(f"/api/tickets/{ticket_id}/priority", headers=it, json={"priority": "Urgent"}).json()["priority_history"] == [event]

    hr_ticket = client.post("/api/tickets", headers=employee, json={
        "title": "Leave balance question", "description": "Need current leave balance",
        "impact": "Planning only; work is not blocked", "category": "HR",
    }).json()
    admin_change = client.patch(f"/api/tickets/{hr_ticket['id']}/priority", headers=admin, json={"priority": "Urgent"})
    assert admin_change.status_code == 200
    assert admin_change.json()["priority_history"][0]["actor_email"] == "admin@example.test"
