"""
TCP-клиент тарифов. Вариант 20: специализированная команда — поиск по скорости.
"""

import json
import socket
import sys

from protocol import ProtocolError, decode, encode

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")

HOST = "127.0.0.1"
TCP_PORT = 19020
UDP_PORT = 19021


def read_line(prompt):
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


class TariffClient:
    def __init__(self, host=HOST, port=TCP_PORT, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock.settimeout(self.timeout)

    def request(self, payload: dict) -> dict:
        if self.sock is None:
            raise ProtocolError("нет соединения")
        self.sock.sendall(encode(payload))
        buffer = ""
        while "\n" not in buffer:
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout as exc:
                raise TimeoutError("сервер не ответил за отведённое время") from exc
            if not chunk:
                raise ConnectionError("сервер закрыл соединение")
            buffer += chunk.decode("utf-8")
        line = buffer.split("\n", 1)[0]
        return decode(line)

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None


def udp_search(min_speed: int) -> dict:
    payload = encode({"cmd": "search_speed", "min_speed": min_speed})
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(2)
        sock.sendto(payload.strip(), (HOST, UDP_PORT))
        data, _ = sock.recvfrom(8192)
        return json.loads(data.decode("utf-8"))


def show(response):
    print(json.dumps(response, ensure_ascii=False, indent=2))


def print_menu():
    print()
    print("===== Клиент тарифов =====")
    print("1. Получить список")
    print("2. Получить объект")
    print("3. Создать")
    print("4. Изменить")
    print("5. Удалить")
    print("6. Поиск тарифов по скорости")
    print("7. Ping")
    print("8. UDP-поиск по скорости")
    print("0. Выход")
    print()


def main():
    client = TariffClient()
    try:
        client.connect()
    except OSError as exc:
        print(f"Не удалось подключиться к {HOST}:{TCP_PORT}: {exc}")
        print("Сначала запустите server.py")
        return
    print(f"Подключено к {HOST}:{TCP_PORT}")

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            if choice == "1":
                show(client.request({"cmd": "list"}))
            elif choice == "2":
                item_id = int(read_line("ID: "))
                show(client.request({"cmd": "get", "id": item_id}))
            elif choice == "3":
                name = read_line("Название: ")
                speed = int(read_line("Скорость: "))
                price = float(read_line("Цена: ").replace(",", "."))
                region = read_line("Регион: ")
                show(client.request({
                    "cmd": "create", "name": name, "speed": speed,
                    "price": price, "region": region,
                }))
            elif choice == "4":
                item_id = int(read_line("ID: "))
                price = float(read_line("Новая цена: ").replace(",", "."))
                show(client.request({"cmd": "update", "id": item_id, "price": price}))
            elif choice == "5":
                item_id = int(read_line("ID: "))
                show(client.request({"cmd": "delete", "id": item_id}))
            elif choice == "6":
                speed = int(read_line("Минимальная скорость: "))
                show(client.request({"cmd": "search_speed", "min_speed": speed}))
            elif choice == "7":
                show(client.request({"cmd": "ping"}))
            elif choice == "8":
                speed = int(read_line("Минимальная скорость: "))
                print("UDP не гарантирует доставку. Для справочного поиска это допустимо:")
                print("повторный запрос дешевле, чем держать соединение учёта тарифов.")
                show(udp_search(speed))
            elif choice == "0":
                print("Работа клиента завершена.")
                break
            else:
                print("Ошибка: выберите пункт от 0 до 8.")
        except (ValueError, ProtocolError, TimeoutError, ConnectionError, OSError) as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            break
    client.close()


if __name__ == "__main__":
    main()
