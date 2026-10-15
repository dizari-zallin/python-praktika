"""
Лабораторная работа №20. Вариант 20.
Планировщик задач. Рядом лежат Dockerfile, docker-compose и CI.
"""

import sys

from scheduler import Scheduler

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


def main():
    scheduler = Scheduler()
    print("Очередь задач в Redis. Если REDIS_URL не задан, используется локальный совместимый сервер.")
    while True:
        print()
        print("===== Планировщик =====")
        print("1. Добавить задачу")
        print("2. Показать очередь")
        print("3. Выполнить подошедшие задачи")
        print("0. Выход")
        choice = read_line("Выберите действие: ")
        if choice == "1":
            title = read_line("Название: ")
            run_at = read_line("Когда (ГГГГ-ММ-ДД ЧЧ:ММ): ")
            job = scheduler.add(title, run_at)
            print("Добавлено:", job)
        elif choice == "2":
            jobs = scheduler.list_jobs()
            if not jobs:
                print("Очередь пуста.")
            for index, job in enumerate(jobs, start=1):
                print(f"{index}. {job['run_at']} {job['title']} — {job['status']}")
        elif choice == "3":
            now = read_line("Текущее время (ГГГГ-ММ-ДД ЧЧ:ММ): ")
            done = scheduler.run_due(now)
            if not done:
                print("Подошедших задач нет.")
            for job in done:
                print("Выполнено:", job["title"])
        elif choice == "0":
            print("Работа программы завершена.")
            break
        else:
            print("Ошибка: выберите пункт от 0 до 3.")


if __name__ == "__main__":
    main()
