"""
TCP-сервер тарифов. Несколько клиентов обслуживаются в отдельных потоках.
UDP-порт отвечает на поиск по скорости: для справочного запроса потеря пакета допустима.
"""

import logging
import os
import socket
import sys
import threading

from protocol import ProtocolError, decode, encode, fail, ok
from repository import TariffRepository

BASE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE, "server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("tariff-server")


class TariffServer:
    def __init__(self, host="127.0.0.1", tcp_port=19020, udp_port=19021):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.repository = TariffRepository()
        self.repository.seed()
        self._stop = threading.Event()

    # Одна и та же обработка команд для TCP и UDP, чтобы правила тарифов не разъехались.
    def handle_command(self, message: dict) -> dict:
        cmd = message.get("cmd")
        try:
            if cmd == "ping":
                return ok("pong")
            if cmd == "list":
                return ok([item.to_dict() for item in self.repository.all()])
            if cmd == "get":
                item = self.repository.get(int(message["id"]))
                if item is None:
                    return fail("тариф не найден")
                return ok(item.to_dict())
            if cmd == "create":
                item = self.repository.add(
                    message["name"],
                    int(message["speed"]),
                    float(message["price"]),
                    message.get("region", "Москва"),
                )
                return ok(item.to_dict())
            if cmd == "update":
                fields = {}
                for key in ("name", "speed", "price", "region"):
                    if key in message:
                        fields[key] = message[key]
                if "speed" in fields:
                    fields["speed"] = int(fields["speed"])
                if "price" in fields:
                    fields["price"] = float(fields["price"])
                item = self.repository.update(int(message["id"]), **fields)
                if item is None:
                    return fail("тариф не найден")
                return ok(item.to_dict())
            if cmd == "delete":
                if not self.repository.delete(int(message["id"])):
                    return fail("тариф не найден")
                return ok("удалён")
            # Специализированная команда варианта: тарифы не медленнее заданной скорости.
            if cmd == "search_speed":
                found = self.repository.by_speed(int(message["min_speed"]))
                return ok([item.to_dict() for item in found])
            return fail("неизвестная команда")
        except (KeyError, TypeError, ValueError) as exc:
            return fail(f"некорректные поля: {exc}")

    # Один клиент в своём потоке. Сообщение собирается до перевода строки, потому что TCP отдаёт байты частями.
    def serve_client(self, conn: socket.socket, address):
        log.info("Client connected: %s:%s", address[0], address[1])
        conn.settimeout(30)
        buffer = ""
        try:
            while not self._stop.is_set():
                try:
                    chunk = conn.recv(4096)
                except socket.timeout:
                    log.info("Timeout: %s:%s", address[0], address[1])
                    conn.sendall(encode(fail("тайм-аут ожидания команды")))
                    break
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    log.info("Command: %s", line.strip()[:120])
                    try:
                        message = decode(line)
                        response = self.handle_command(message)
                    except ProtocolError as exc:
                        response = fail(str(exc))
                    conn.sendall(encode(response))
        except OSError as exc:
            log.info("Client error %s: %s", address, exc)
        finally:
            conn.close()
            log.info("Client disconnected: %s:%s", address[0], address[1])

    def tcp_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.tcp_port))
            server.listen()
            server.settimeout(0.5)
            log.info("TCP %s:%s", self.host, self.tcp_port)
            while not self._stop.is_set():
                try:
                    conn, address = server.accept()
                except socket.timeout:
                    continue
                thread = threading.Thread(target=self.serve_client, args=(conn, address), daemon=True)
                thread.start()

    # Справочный UDP-запрос. Потеря датаграммы не портит учёт тарифов на TCP.
    def udp_loop(self):
        """Справочный UDP-запрос. Потеря датаграммы не ломает учёт тарифов."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.udp_port))
            sock.settimeout(0.5)
            log.info("UDP %s:%s", self.host, self.udp_port)
            while not self._stop.is_set():
                try:
                    data, address = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                message = {}
                try:
                    message = decode(data.decode("utf-8"))
                    response = self.handle_command(message)
                except ProtocolError as exc:
                    response = fail(str(exc))
                log.info("UDP %s from %s", message.get("cmd", "?"), address)
                sock.sendto(encode(response).strip(), address)

    def start(self):
        threading.Thread(target=self.tcp_loop, daemon=True).start()
        threading.Thread(target=self.udp_loop, daemon=True).start()

    def stop(self):
        self._stop.set()


def main():
    server = TariffServer()
    log.info("Сервер тарифов запущен. Остановка: Ctrl+C")
    server.start()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.stop()
        log.info("Сервер остановлен")


if __name__ == "__main__":
    main()
