"""Консольный клиент FastAPI тарифов."""

import json
import sys

import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:5014"


def read_line(prompt):
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


def show(response: httpx.Response):
    print(f"HTTP {response.status_code}")
    if response.content:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))


def main():
    try:
        httpx.get(BASE + "/tariffs", timeout=3)
    except httpx.HTTPError as exc:
        print("Сервер не запущен. Команда: python -m uvicorn app:app --port 5014")
        print(exc)
        return
    client = httpx.Client(base_url=BASE, timeout=5)
    actions = {
        "1": lambda: show(client.get("/tariffs")),
        "2": lambda: show(client.get(f"/tariffs/{read_line('ID: ')}")),
        "3": lambda: show(client.post("/tariffs", json={
            "name": read_line("Название: "),
            "speed": int(read_line("Скорость: ")),
            "price": float(read_line("Цена: ")),
            "traffic": read_line("Трафик: ") or "безлимит",
            "services": ["антивирус"],
            "region": read_line("Регион: ") or "Москва",
            "status": "активен",
        })),
        "4": lambda: show(client.patch(f"/tariffs/{read_line('ID: ')}", json={
            "price": float(read_line("Новая цена: ")),
        })),
        "5": lambda: show(client.get("/tariffs/by-speed", params={"min_speed": read_line("Мин. скорость: ")})),
        "6": lambda: show(client.get("/tariffs", params={"sort": "price"})),
        "7": lambda: show(client.delete(f"/tariffs/{read_line('ID: ')}")),
    }
    while True:
        print()
        print("===== FastAPI /tariffs =====")
        print("1. Список  2. Объект  3. Создать  4. Изменить цену")
        print("5. По скорости  6. Сортировка по цене  7. Удалить  0. Выход")
        choice = read_line("Выберите действие: ")
        if choice == "0":
            print("Работа клиента завершена.")
            break
        action = actions.get(choice)
        if action is None:
            print("Ошибка: неизвестный пункт.")
            continue
        try:
            action()
        except (httpx.HTTPError, ValueError) as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            break


if __name__ == "__main__":
    main()
