"""Планировщик задач. Очередь хранится в Redis."""

import json
import os
from datetime import datetime

import fakeredis


def connect():
    url = os.environ.get("REDIS_URL", "")
    if url:
        import redis
        return redis.Redis.from_url(url, decode_responses=True)
    return fakeredis.FakeRedis(decode_responses=True)


class Scheduler:
    def __init__(self, client=None):
        self.client = client or connect()

    def add(self, title, run_at):
        job = {"title": title, "run_at": run_at, "status": "ожидает"}
        self.client.rpush("jobs", json.dumps(job, ensure_ascii=False))
        return job

    def list_jobs(self):
        raw = self.client.lrange("jobs", 0, -1)
        return [json.loads(item) for item in raw]

    # В «выполнено» переходят только задачи, время которых уже наступило. Остальные остаются в очереди.
    def run_due(self, now=None):
        moment = now or datetime.now().strftime("%Y-%m-%d %H:%M")
        jobs = self.list_jobs()
        done = []
        self.client.delete("jobs")
        for job in jobs:
            if job["status"] == "ожидает" and job["run_at"] <= moment:
                job["status"] = "выполнено"
                done.append(job)
            self.client.rpush("jobs", json.dumps(job, ensure_ascii=False))
        return done
