"""Консольный HTTP-клиент лабораторной работы №10."""

import json
import sys

import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:5010"
HEADERS = {"X-API-Key": "lab10-key"}


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
        try:
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print(response.text)
    else:
        print("(пустое тело)")


def print_menu():
    print()
    print("===== HTTP-клиент тарифов =====")
    print("1. Получить список")
    print("2. Получить объект")
    print("3. Создать")
    print("4. Изменить (PUT)")
    print("5. Частично изменить (PATCH)")
    print("6. Удалить")
    print("7. Фильтрация по статусу")
    print("8. Сортировка по цене")
    print("9. Тарифы по скорости")
    print("0. Выход")
    print()


def main():
    client = httpx.Client(base_url=BASE, headers=HEADERS, timeout=5)
    try:
        health = httpx.get(BASE + "/health", timeout=3)
        print("Сервер:", health.json())
    except httpx.HTTPError as exc:
        print("Сервер не запущен:", exc)
        print("Запустите: python app.py")
        return

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            if choice == "1":
                show(client.get("/tariffs"))
            elif choice == "2":
                show(client.get(f"/tariffs/{read_line('ID: ')}"))
            elif choice == "3":
                payload = {
                    "name": read_line("Название: "),
                    "speed": int(read_line("Скорость: ")),
                    "price": float(read_line("Цена: ").replace(",", ".")),
                    "region": read_line("Регион: "),
                    "traffic": "безлимит",
                }
                show(client.post("/tariffs", json=payload))
            elif choice == "4":
                item_id = read_line("ID: ")
                payload = {
                    "name": read_line("Название: "),
                    "speed": int(read_line("Скорость: ")),
                    "price": float(read_line("Цена: ").replace(",", ".")),
                    "region": read_line("Регион: "),
                    "status": "активен",
                }
                show(client.put(f"/tariffs/{item_id}", json=payload))
            elif choice == "5":
                item_id = read_line("ID: ")
                price = float(read_line("Новая цена: ").replace(",", "."))
                show(client.patch(f"/tariffs/{item_id}", json={"price": price}))
            elif choice == "6":
                show(client.delete(f"/tariffs/{read_line('ID: ')}"))
            elif choice == "7":
                show(client.get("/tariffs", params={"status": "активен"}))
            elif choice == "8":
                show(client.get("/tariffs", params={"sort": "price"}))
            elif choice == "9":
                speed = read_line("Минимальная скорость: ")
                show(client.get("/tariffs/by-speed", params={"min_speed": speed}))
            elif choice == "0":
                print("Работа клиента завершена.")
                break
            else:
                print("Ошибка: выберите пункт от 0 до 9.")
        except (httpx.HTTPError, ValueError) as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            break
    client.close()


if __name__ == "__main__":
    main()
