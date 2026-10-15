"""Последовательный запуск трёх сервисов и смена статуса задачи."""

import sys

import httpx
import uvicorn

from notify_app import create_app as notify_app
from tasks_app import create_app as tasks_app
from users_app import create_app as users_app

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    print("Сервисы: users :8019, tasks :8020, notifications :8021")
    print("Демонстрация идёт через TestClient-совместимые вызовы внутри процесса")
    print("и через HTTP, если серверы уже подняты отдельными командами.")
    users = users_app()
    tasks = tasks_app("http://notify.local")
    notes = notify_app()
    from fastapi.testclient import TestClient

    users_client = TestClient(users)
    notes_client = TestClient(notes)

    class LocalNotify:
        def post(self, url, json, timeout):
            response = notes_client.post("/events", json=json)
            response.raise_for_status()
            return response

    import tasks_app as tasks_module
    original = tasks_module.httpx.post
    tasks_module.httpx.post = LocalNotify().post
    tasks = tasks_app("http://notify.local")
    tasks_client = TestClient(tasks)
    try:
        user = users_client.post("/users", json={"name": "Иванов", "email": "ivan@example.com"}).json()
        print("Пользователь:", user)
        task = tasks_client.post("/tasks", json={"title": "Проверить канал", "assignee": user["name"]}).json()
        print("Задача:", task)
        updated = tasks_client.post(f"/tasks/{task['id']}/status", json={"status": "в работе"}).json()
        print("После смены статуса:", updated)
        print("События уведомлений:", notes_client.get("/events").json())
    finally:
        tasks_module.httpx.post = original
    print("Цепочка users → tasks → notifications выполнена.")


if __name__ == "__main__":
    main()
