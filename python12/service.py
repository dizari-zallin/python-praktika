"""Операции SQLAlchemy. Назначение задачи меняет задачу и проект в одной транзакции."""

import os

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Base, Project, Task, User

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "tasks.db")


def make_engine(path=None):
    target = path or DB_PATH
    folder = os.path.dirname(target)
    if folder:
        os.makedirs(folder, exist_ok=True)
    engine = create_engine(f"sqlite:///{target}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def seed(session: Session):
    if session.scalar(select(User).limit(1)):
        return
    ivan = User(name="Иванов", email="ivan@example.com")
    anna = User(name="Петрова", email="anna@example.com")
    session.add_all([ivan, anna])
    session.flush()
    site = Project(title="Сайт провайдера", owner=ivan)
    billing = Project(title="Биллинг", owner=anna)
    session.add_all([site, billing])
    session.flush()
    session.add(Task(title="Макет главной", status="новая", project=site, assignee=anna))
    session.add(Task(title="Оплата тарифа", status="в работе", project=billing, assignee=ivan))
    session.commit()


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def users(self):
        return list(self.session.scalars(select(User).order_by(User.name)))

    def projects(self):
        return list(self.session.scalars(select(Project).order_by(Project.title)))

    def tasks(self, status=None, project_title=None, order="title"):
        query = select(Task)
        if status:
            query = query.where(Task.status == status)
        if project_title:
            query = query.join(Project).where(Project.title == project_title)
        if order == "status":
            query = query.order_by(Task.status, Task.title)
        else:
            query = query.order_by(Task.title)
        return list(self.session.scalars(query))

    def create_user(self, name, email):
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        return user

    # Проект и первая задача пишутся одной транзакцией: незавершённая пара не сохраняется.
    def create_project_with_task(self, owner_email, project_title, task_title):
        """Атомарно: проект без первой задачи не сохраняется."""
        owner = self.session.scalar(select(User).where(User.email == owner_email))
        if owner is None:
            raise ValueError("пользователь не найден")
        try:
            project = Project(title=project_title, owner=owner)
            task = Task(title=task_title, status="новая", project=project, assignee=owner)
            self.session.add(project)
            self.session.add(task)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return project

    # Назначение меняет и исполнителя, и статус задачи.
    def assign(self, task_id, email):
        task = self.session.get(Task, task_id)
        user = self.session.scalar(select(User).where(User.email == email))
        if task is None or user is None:
            raise ValueError("задача или пользователь не найдены")
        task.assignee = user
        task.status = "назначена"
        self.session.commit()
        return task

    def find_tasks(self, text):
        return list(
            self.session.scalars(select(Task).where(Task.title.contains(text)).order_by(Task.title))
        )
