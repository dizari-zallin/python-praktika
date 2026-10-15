import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import create_app
from models import Base, Project, User


def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 't.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(User(name="Иванов"))
        session.add(Project(title="Сайт"))
        session.commit()
    return TestClient(create_app(engine))


def test_create_with_priority_and_deadline(tmp_path):
    api = client(tmp_path)
    response = api.post("/tasks", json={
        "title": "Вёрстка", "project_id": 1, "assignee_id": 1,
        "priority": "высокий", "deadline": "2026-10-05",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["assignee"] == "Иванов"
    assert body["deadline"] == "2026-10-05"
    assert body["priority"] == "высокий"


def test_comment_and_status(tmp_path):
    api = client(tmp_path)
    created = api.post("/tasks", json={
        "title": "API", "project_id": 1, "assignee_id": 1, "priority": "средний",
    }).json()
    status = api.post(f"/tasks/{created['id']}/status", json={"status": "в работе"})
    comment = api.post(f"/tasks/{created['id']}/comments", json={"text": "взял в работу", "author": "Иванов"})
    assert status.json()["status"] == "в работе"
    assert comment.json()["comments"][0]["text"] == "взял в работу"


def test_page_lists_task(tmp_path):
    api = client(tmp_path)
    api.post("/tasks", json={"title": "Отчёт", "project_id": 1, "assignee_id": 1})
    page = api.get("/")
    assert page.status_code == 200
    assert "Отчёт" in page.text
