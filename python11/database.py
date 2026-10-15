"""SQLite-схема тарифов. SQL написан вручную, запросы параметризованы."""

import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "provider.db")


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS tariffs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            speed INTEGER NOT NULL,
            price REAL NOT NULL,
            region_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tariff_services (
            tariff_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            PRIMARY KEY (tariff_id, service_id),
            FOREIGN KEY (tariff_id) REFERENCES tariffs(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );
        CREATE INDEX IF NOT EXISTS idx_tariffs_speed ON tariffs(speed);
        CREATE INDEX IF NOT EXISTS idx_tariffs_region ON tariffs(region_id);
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM tariffs").fetchone()[0]
    if count:
        return
    regions = ["Москва", "Казань", "Тула"]
    for name in regions:
        conn.execute("INSERT INTO regions(name) VALUES (?)", (name,))
    services = [("белый IP", 200), ("статический IP", 150), ("антивирус", 100), ("ТВ", 250)]
    for name, price in services:
        conn.execute("INSERT INTO services(name, price) VALUES (?, ?)", (name, price))
    samples = [
        ("Домашний 50", 50, 350, 1, "активен"),
        ("Домашний 100", 100, 500, 1, "активен"),
        ("Домашний 300", 300, 800, 1, "активен"),
        ("Домашний 500", 500, 1100, 2, "активен"),
        ("Корпоративный 100", 100, 1500, 2, "активен"),
        ("Корпоративный 500", 500, 2500, 1, "активен"),
        ("Мобильный 20", 20, 250, 3, "активен"),
        ("Мобильный 50", 50, 400, 3, "архив"),
        ("Ночной 100", 100, 300, 3, "активен"),
        ("Безлимит 1 Гбит", 1000, 1800, 1, "активен"),
        ("Архивный 10", 10, 150, 2, "архив"),
    ]
    for row in samples:
        conn.execute(
            "INSERT INTO tariffs(name, speed, price, region_id, status) VALUES (?, ?, ?, ?, ?)",
            row,
        )
    links = [(2, 1), (2, 3), (6, 1), (6, 2), (10, 4), (4, 3)]
    for tariff_id, service_id in links:
        conn.execute(
            "INSERT INTO tariff_services(tariff_id, service_id) VALUES (?, ?)",
            (tariff_id, service_id),
        )
    conn.commit()


# Набор запросов из методички. Значения передаются параметрами ?, а не склейкой строки.
def showcase_queries(conn):
    """Набор запросов, который требует методичка."""
    queries = [
        ("SELECT", "SELECT id, name, speed, price FROM tariffs"),
        ("WHERE", "SELECT name, price FROM tariffs WHERE status = ?", ("активен",)),
        ("ORDER BY", "SELECT name, speed FROM tariffs ORDER BY speed DESC"),
        (
            "JOIN",
            """
            SELECT t.name, r.name AS region
            FROM tariffs t JOIN regions r ON r.id = t.region_id
            """,
        ),
        (
            "LEFT JOIN",
            """
            SELECT t.name, s.name
            FROM tariffs t
            LEFT JOIN tariff_services ts ON ts.tariff_id = t.id
            LEFT JOIN services s ON s.id = ts.service_id
            """,
        ),
        (
            "GROUP BY",
            """
            SELECT r.name, COUNT(t.id) AS cnt
            FROM regions r LEFT JOIN tariffs t ON t.region_id = r.id
            GROUP BY r.name
            """,
        ),
        (
            "HAVING",
            """
            SELECT r.name, COUNT(t.id) AS cnt
            FROM regions r JOIN tariffs t ON t.region_id = r.id
            GROUP BY r.name
            HAVING COUNT(t.id) >= 3
            """,
        ),
        ("COUNT", "SELECT COUNT(*) FROM tariffs"),
        ("AVG", "SELECT AVG(price) FROM tariffs WHERE status = ?", ("активен",)),
        ("подзапрос", "SELECT name FROM tariffs WHERE price > (SELECT AVG(price) FROM tariffs)"),
        (
            "несколько условий",
            "SELECT name, speed, price FROM tariffs WHERE speed >= ? AND status = ?",
            (100, "активен"),
        ),
    ]
    report = []
    for item in queries:
        title, sql = item[0], item[1]
        params = item[2] if len(item) > 2 else ()
        rows = conn.execute(sql, params).fetchall()
        preview = [tuple(row) for row in rows[:4]]
        report.append((title, len(rows), preview))
    return report


# Тариф и связь с услугой фиксируются вместе. Ошибка на втором шаге откатывает и первый.
def add_tariff_with_service(conn, name, speed, price, region_name, service_name):
    """Транзакция: тариф и связь с услугой фиксируются вместе."""
    try:
        region = conn.execute("SELECT id FROM regions WHERE name = ?", (region_name,)).fetchone()
        service = conn.execute("SELECT id FROM services WHERE name = ?", (service_name,)).fetchone()
        if region is None or service is None:
            raise ValueError("регион или услуга не найдены")
        cursor = conn.execute(
            "INSERT INTO tariffs(name, speed, price, region_id, status) VALUES (?, ?, ?, ?, ?)",
            (name, speed, price, region["id"], "активен"),
        )
        conn.execute(
            "INSERT INTO tariff_services(tariff_id, service_id) VALUES (?, ?)",
            (cursor.lastrowid, service["id"]),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise


def explain_index(conn):
    plan = conn.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM tariffs WHERE speed >= ?",
        (100,),
    ).fetchall()
    return [tuple(row) for row in plan]
