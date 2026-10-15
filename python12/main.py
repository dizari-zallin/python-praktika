"""
Лабораторная работа №12. Вариант 20.
Система задач на SQLAlchemy.
"""

import sys

from service import TaskService, make_engine, seed
from sqlalchemy.orm import Session

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")


def read_line(prompt):
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


def show_tasks(tasks):
    if not tasks:
        print("Задач нет.")
        return
    print(f"{'ID':<5}{'Задача':<24}{'Статус':<14}{'Проект':<22}{'Исполнитель'}")
    for task in tasks:
        assignee = task.assignee.name if task.assignee else "—"
        print(f"{task.id:<5}{task.title:<24}{task.status:<14}{task.project.title:<22}{assignee}")


def print_menu():
    print()
    print("===== Задачи (SQLAlchemy) =====")
    print("1. Пользователи")
    print("2. Проекты и задачи владельца")
    print("3. Все задачи")
    print("4. Создать пользователя")
    print("5. Создать проект с первой задачей")
    print("6. Назначить исполнителя")
    print("7. Поиск по названию")
    print("8. Фильтр по статусу")
    print("9. Сортировка по статусу")
    print("0. Выход")
    print()


def main():
    engine = make_engine()
    with Session(engine) as session:
        seed(session)
        service = TaskService(session)
        print("База tasks.db готова, связи User — Project — Task загружены.")
        while True:
            print_menu()
            choice = read_line("Выберите действие: ")
            try:
                if choice == "1":
                    for user in service.users():
                        print(f"#{user.id} {user.name} <{user.email}>, проектов: {len(user.projects)}")
                elif choice == "2":
                    for project in service.projects():
                        print(f"\n{project.title} — владелец {project.owner.name}")
                        for task in project.tasks:
                            print(f"  - {task.title} [{task.status}]")
                elif choice == "3":
                    show_tasks(service.tasks())
                elif choice == "4":
                    user = service.create_user(read_line("Имя: "), read_line("Email: "))
                    print(f"Создан пользователь #{user.id}")
                elif choice == "5":
                    project = service.create_project_with_task(
                        read_line("Email владельца: "),
                        read_line("Название проекта: "),
                        read_line("Первая задача: "),
                    )
                    print(f"Проект #{project.id} и задача сохранены одной транзакцией.")
                elif choice == "6":
                    task = service.assign(int(read_line("ID задачи: ")), read_line("Email исполнителя: "))
                    print(f"Задача «{task.title}» назначена, статус: {task.status}")
                elif choice == "7":
                    show_tasks(service.find_tasks(read_line("Фрагмент названия: ")))
                elif choice == "8":
                    show_tasks(service.tasks(status=read_line("Статус: ")))
                elif choice == "9":
                    show_tasks(service.tasks(order="status"))
                elif choice == "0":
                    print("Работа программы завершена.")
                    break
                else:
                    print("Ошибка: выберите пункт от 0 до 9.")
            except ValueError as exc:
                print(f"Ошибка: {exc}")
            except EOFError:
                break


if __name__ == "__main__":
    main()
