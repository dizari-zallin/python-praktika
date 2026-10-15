"""
Лабораторная работа №21. Вариант 20.
Система задач: пользователь, проект, задача, комментарий.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Base, Comment, Project, Task, User

BASE = os.path.dirname(os.path.abspath(__file__))
ENGINE = create_engine(f"sqlite:///{os.path.join(BASE, 'data', 'tasks.db')}", echo=False)


class TaskIn(BaseModel):
    title: str
    project_id: int
    assignee_id: int
    priority: str = "средний"
    deadline: str = ""


class StatusIn(BaseModel):
    status: str


class CommentIn(BaseModel):
    text: str
    author: str


def seed(session: Session):
    if session.scalar(select(User).limit(1)):
        return
    ivan = User(name="Иванов")
    anna = User(name="Петрова")
    session.add_all([ivan, anna])
    site = Project(title="Сайт провайдера")
    billing = Project(title="Биллинг")
    session.add_all([site, billing])
    session.flush()
    session.add(Task(
        title="Макет главной", priority="высокий", status="новая",
        deadline="2026-10-01", project=site, assignee=anna,
    ))
    session.add(Task(
        title="Списание абонентской платы", priority="средний", status="в работе",
        deadline="2026-09-30", project=billing, assignee=ivan,
    ))
    session.commit()


def task_dict(task: Task):
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "status": task.status,
        "deadline": task.deadline,
        "project": task.project.title,
        "assignee": task.assignee.name if task.assignee else "",
        "comments": [{"author": item.author, "text": item.text} for item in task.comments],
    }


def create_app(engine=None):
    db = engine or ENGINE
    os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
    Base.metadata.create_all(db)
    with Session(db) as session:
        seed(session)
    app = FastAPI(title="Система задач")

    @app.get("/", response_class=HTMLResponse)
    def page():
        with Session(db) as session:
            tasks = session.scalars(select(Task)).all()
            rows = "".join(
                f"<tr><td>{task.id}</td><td>{task.title}</td><td>{task.project.title}</td>"
                f"<td>{task.assignee.name if task.assignee else ''}</td>"
                f"<td>{task.priority}</td><td>{task.status}</td><td>{task.deadline}</td></tr>"
                for task in tasks
            )
        return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>Задачи</title>
        <style>body{{font-family:Segoe UI,sans-serif;margin:32px}}table{{border-collapse:collapse;width:100%}}
        td,th{{border-bottom:1px solid #ddd;padding:8px;text-align:left}}th{{background:#16324f;color:white}}</style>
        </head><body><h1>Система управления задачами</h1>
        <p>Пользователь, проект, задача и комментарий. У задачи есть приоритет, статус, исполнитель и дедлайн.</p>
        <table><tr><th>ID</th><th>Задача</th><th>Проект</th><th>Исполнитель</th><th>Приоритет</th><th>Статус</th><th>Дедлайн</th></tr>
        {rows}</table></body></html>"""

    @app.get("/tasks")
    def list_tasks():
        with Session(db) as session:
            tasks = session.scalars(select(Task)).all()
            return [task_dict(task) for task in tasks]

    # Задача создаётся только для существующего проекта и исполнителя и с одним из трёх приоритетов.
    @app.post("/tasks", status_code=201)
    def create_task(payload: TaskIn):
        with Session(db) as session:
            project = session.get(Project, payload.project_id)
            assignee = session.get(User, payload.assignee_id)
            if project is None or assignee is None:
                raise HTTPException(400, "проект или исполнитель не найден")
            if payload.priority not in {"низкий", "средний", "высокий"}:
                raise HTTPException(400, "приоритет: низкий, средний или высокий")
            task = Task(
                title=payload.title, priority=payload.priority, deadline=payload.deadline,
                project=project, assignee=assignee,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task_dict(task)

    @app.post("/tasks/{task_id}/status")
    def set_status(task_id: int, payload: StatusIn):
        with Session(db) as session:
            task = session.get(Task, task_id)
            if task is None:
                raise HTTPException(404, "задача не найдена")
            task.status = payload.status
            session.commit()
            return task_dict(task)

    # Комментарий привязывается к задаче и не существует отдельно от неё.
    @app.post("/tasks/{task_id}/comments", status_code=201)
    def add_comment(task_id: int, payload: CommentIn):
        with Session(db) as session:
            task = session.get(Task, task_id)
            if task is None:
                raise HTTPException(404, "задача не найдена")
            session.add(Comment(text=payload.text, author=payload.author, task=task))
            session.commit()
            session.refresh(task)
            return task_dict(task)

    return app


app = create_app()
