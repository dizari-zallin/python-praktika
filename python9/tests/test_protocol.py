import os
import socket
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol import decode, encode
from server import TariffServer


def test_roundtrip():
    server = TariffServer(tcp_port=19120, udp_port=19121)
    server.start()
    time.sleep(0.3)
    try:
        with socket.create_connection(("127.0.0.1", 19120), timeout=2) as sock:
            sock.sendall(encode({"cmd": "search_speed", "min_speed": 300}))
            raw = sock.recv(4096).decode("utf-8")
        response = decode(raw.strip())
        assert response["ok"] is True
        speeds = [item["speed"] for item in response["data"]]
        assert speeds == [300, 500]
    finally:
        server.stop()


def test_missing_tariff():
    server = TariffServer(tcp_port=19122, udp_port=19123)
    server.start()
    time.sleep(0.3)
    try:
        with socket.create_connection(("127.0.0.1", 19122), timeout=2) as sock:
            sock.sendall(encode({"cmd": "get", "id": 99}))
            raw = sock.recv(4096).decode("utf-8")
        response = decode(raw.strip())
        assert response["ok"] is False
    finally:
        server.stop()


def test_two_clients():
    server = TariffServer(tcp_port=19124, udp_port=19125)
    server.start()
    time.sleep(0.3)
    results = []

    def worker():
        with socket.create_connection(("127.0.0.1", 19124), timeout=2) as sock:
            sock.sendall(encode({"cmd": "ping"}))
            results.append(sock.recv(1024).decode("utf-8"))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    server.stop()
    assert len(results) == 2
    assert all("pong" in item for item in results)
