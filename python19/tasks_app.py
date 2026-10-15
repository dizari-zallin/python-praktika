"""Сервис задач. При смене статуса отправляет событие в сервис уведомлений."""

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class TaskIn(BaseModel):
    title: str
    assignee: str


class StatusIn(BaseModel):
    status: str


def create_app(notify_url="http://127.0.0.1:8021"):
    app = FastAPI(title="tasks")
    tasks = {}
    seq = {"n": 1}

    @app.get("/health")
    def health():
        return {"service": "tasks"}

    @app.post("/tasks", status_code=201)
    def create_task(payload: TaskIn):
        item = {
            "id": seq["n"],
            "title": payload.title,
            "assignee": payload.assignee,
            "status": "новая",
        }
        seq["n"] += 1
        tasks[item["id"]] = item
        return item

    @app.get("/tasks")
    def list_tasks():
        return list(tasks.values())

    # После смены статуса уходит событие в сервис уведомлений. Если тот недоступен, статус всё равно сохраняется.
    @app.post("/tasks/{task_id}/status")
    def change_status(task_id: int, payload: StatusIn):
        item = tasks.get(task_id)
        if item is None:
            raise HTTPException(404, "задача не найдена")
        item["status"] = payload.status
        event = {
            "task_id": item["id"],
            "title": item["title"],
            "status": item["status"],
            "assignee": item["assignee"],
        }
        try:
            httpx.post(f"{notify_url}/events", json=event, timeout=2)
            item["event"] = "отправлено"
        except httpx.HTTPError:
            item["event"] = "сервис уведомлений недоступен"
        return item

    return app


app = create_app()
