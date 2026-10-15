import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service import TaskService, make_engine, seed
from sqlalchemy.orm import Session


def service(tmp_path):
    engine = make_engine(str(tmp_path / "t.db"))
    session = Session(engine)
    seed(session)
    return TaskService(session), session


def test_seed_relations(tmp_path):
    svc, session = service(tmp_path)
    projects = svc.projects()
    assert projects[0].owner.name
    assert projects[0].tasks
    session.close()


def test_filter_and_sort(tmp_path):
    svc, session = service(tmp_path)
    found = svc.tasks(status="в работе")
    assert len(found) == 1
    ordered = svc.tasks(order="status")
    assert ordered
    session.close()


def test_search(tmp_path):
    svc, session = service(tmp_path)
    assert svc.find_tasks("Оплата")
    session.close()


def test_transaction_creates_task(tmp_path):
    svc, session = service(tmp_path)
    project = svc.create_project_with_task("ivan@example.com", "API", "Контракт")
    assert project.tasks[0].title == "Контракт"
    session.close()


def test_assign(tmp_path):
    svc, session = service(tmp_path)
    task = svc.tasks()[0]
    updated = svc.assign(task.id, "anna@example.com")
    assert updated.status == "назначена"
    assert updated.assignee.email == "anna@example.com"
    session.close()
