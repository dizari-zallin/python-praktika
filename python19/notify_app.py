"""Сервис уведомлений. Принимает событие смены статуса задачи."""

from fastapi import FastAPI
from pydantic import BaseModel


class Event(BaseModel):
    task_id: int
    title: str
    status: str
    assignee: str


def create_app():
    app = FastAPI(title="notifications")
    events = []

    @app.get("/health")
    def health():
        return {"service": "notifications", "events": len(events)}

    @app.post("/events", status_code=202)
    def receive(event: Event):
        events.append(event.model_dump())
        return {"accepted": True}

    @app.get("/events")
    def list_events():
        return events

    return app


app = create_app()
