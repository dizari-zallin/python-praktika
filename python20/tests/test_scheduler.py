import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fakeredis

from scheduler import Scheduler


def test_run_due_only():
    scheduler = Scheduler(fakeredis.FakeRedis(decode_responses=True))
    scheduler.add("Рано", "2026-09-27 10:00")
    scheduler.add("Позже", "2026-09-27 18:00")
    done = scheduler.run_due("2026-09-27 12:00")
    assert [job["title"] for job in done] == ["Рано"]
    titles = {job["title"]: job["status"] for job in scheduler.list_jobs()}
    assert titles["Рано"] == "выполнено"
    assert titles["Позже"] == "ожидает"
