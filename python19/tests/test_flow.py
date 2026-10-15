import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

import tasks_app as tasks_module
from notify_app import create_app as notify_app
from tasks_app import create_app as tasks_app
from users_app import create_app as users_app


def test_status_event_reaches_notifications():
    notes = TestClient(notify_app())

    def fake_post(url, json, timeout):
        return notes.post("/events", json=json)

    original = tasks_module.httpx.post
    tasks_module.httpx.post = fake_post
    try:
        tasks = TestClient(tasks_app())
        created = tasks.post("/tasks", json={"title": "Отчёт", "assignee": "Петрова"})
        assert created.status_code == 201
        changed = tasks.post(f"/tasks/{created.json()['id']}/status", json={"status": "готово"})
        assert changed.status_code == 200
        events = notes.get("/events").json()
        assert events[0]["status"] == "готово"
        assert events[0]["assignee"] == "Петрова"
    finally:
        tasks_module.httpx.post = original


def test_user_created():
    client = TestClient(users_app())
    response = client.post("/users", json={"name": "Иванов", "email": "a@b.c"})
    assert response.status_code == 201
    assert client.get(f"/users/{response.json()['id']}").json()["name"] == "Иванов"
