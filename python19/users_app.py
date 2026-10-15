"""Сервис пользователей."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class UserIn(BaseModel):
    name: str
    email: str


def create_app():
    app = FastAPI(title="users")
    users = {}
    seq = {"n": 1}

    @app.get("/health")
    def health():
        return {"service": "users"}

    @app.post("/users", status_code=201)
    def create_user(payload: UserIn):
        item = {"id": seq["n"], "name": payload.name, "email": payload.email}
        seq["n"] += 1
        users[item["id"]] = item
        return item

    @app.get("/users/{user_id}")
    def get_user(user_id: int):
        item = users.get(user_id)
        if item is None:
            raise HTTPException(404, "пользователь не найден")
        return item

    return app


app = create_app()
