import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from cache_and_docs import PriceCache
from database import add_tariff_with_service, init_db, showcase_queries


def fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "t.db"))
    conn = database.connect()
    init_db(conn)
    return conn


def test_seed_count(tmp_path, monkeypatch):
    conn = fresh(tmp_path, monkeypatch)
    assert conn.execute("SELECT COUNT(*) FROM tariffs").fetchone()[0] >= 10


def test_parameterized_filter(tmp_path, monkeypatch):
    conn = fresh(tmp_path, monkeypatch)
    rows = conn.execute(
        "SELECT name FROM tariffs WHERE status = ? AND speed >= ?",
        ("активен", 500),
    ).fetchall()
    assert rows


def test_transaction_links_service(tmp_path, monkeypatch):
    conn = fresh(tmp_path, monkeypatch)
    item_id = add_tariff_with_service(conn, "Тестовый", 100, 10, "Тула", "ТВ")
    link = conn.execute(
        "SELECT service_id FROM tariff_services WHERE tariff_id = ?",
        (item_id,),
    ).fetchone()
    assert link is not None


def test_queries_run(tmp_path, monkeypatch):
    conn = fresh(tmp_path, monkeypatch)
    report = showcase_queries(conn)
    assert len(report) >= 10


def test_cache_second_hit(tmp_path, monkeypatch):
    calls = {"n": 0}

    def calc():
        calls["n"] += 1
        return 42

    cache = PriceCache()
    cache.get_total("k", calc)
    cache.get_total("k", calc)
    assert calls["n"] == 1
    assert cache.hits == 1
