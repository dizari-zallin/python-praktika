"""
Лабораторная работа №15. Вариант 20.
Веб-приложение учёта проектов и задач на Flask.
"""

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

USERS = [
    {"id": 1, "name": "Иванов"},
    {"id": 2, "name": "Петрова"},
]
PROJECTS = [
    {"id": 1, "title": "Сайт провайдера", "owner_id": 1},
    {"id": 2, "title": "Биллинг", "owner_id": 2},
]
TASKS = [
    {"id": 1, "title": "Макет главной", "project_id": 1, "assignee_id": 2, "status": "новая", "priority": "высокий"},
    {"id": 2, "title": "Оплата тарифа", "project_id": 2, "assignee_id": 1, "status": "в работе", "priority": "средний"},
]
NEXT = {"task": 3, "project": 3}


def user_name(user_id):
    for user in USERS:
        if user["id"] == user_id:
            return user["name"]
    return "—"


def project_title(project_id):
    for project in PROJECTS:
        if project["id"] == project_id:
            return project["title"]
    return "—"


@app.get("/")
def index():
    rows = []
    for task in TASKS:
        rows.append({
            **task,
            "project": project_title(task["project_id"]),
            "assignee": user_name(task["assignee_id"]),
        })
    return render_template("index.html", tasks=rows, projects=PROJECTS, users=USERS)


@app.post("/projects")
def add_project():
    title = request.form.get("title", "").strip()
    owner_id = int(request.form.get("owner_id", 1))
    if title:
        PROJECTS.append({"id": NEXT["project"], "title": title, "owner_id": owner_id})
        NEXT["project"] += 1
    return redirect(url_for("index"))


# Новая задача попадает в список, затем браузер возвращается на главную, чтобы обновление страницы не создало дубль.
@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("index"))
    TASKS.append({
        "id": NEXT["task"],
        "title": title,
        "project_id": int(request.form["project_id"]),
        "assignee_id": int(request.form["assignee_id"]),
        "status": "новая",
        "priority": request.form.get("priority", "средний"),
    })
    NEXT["task"] += 1
    return redirect(url_for("index"))


# Смена статуса выбранной строки таблицы.
@app.post("/tasks/<int:task_id>/status")
def change_status(task_id):
    for task in TASKS:
        if task["id"] == task_id:
            task["status"] = request.form.get("status", task["status"])
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5015, debug=False)
