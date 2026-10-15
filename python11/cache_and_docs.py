"""Документное хранилище расчётов и кэш cache-aside."""

import json
import os

import fakeredis
import mongomock

BASE = os.path.dirname(os.path.abspath(__file__))


class CalculationStore:
    """Документы результатов расчёта. Для запуска без сервера MongoDB используется mongomock."""

    def __init__(self):
        self.client = mongomock.MongoClient()
        self.collection = self.client["provider"]["calculations"]

    def save(self, tariff_name, total, services):
        document = {"tariff": tariff_name, "total": total, "services": services}
        self.collection.insert_one(document)
        return document

    def latest(self, tariff_name):
        return self.collection.find_one({"tariff": tariff_name}, sort=[("_id", -1)])


class PriceCache:
    """Cache-aside: сначала Redis, при промахе — расчёт и запись с TTL."""

    def __init__(self):
        self.client = fakeredis.FakeRedis(decode_responses=True)
        self.hits = 0
        self.misses = 0

    # Сначала кэш. Если ключа нет, значение считается и кладётся с временем жизни 60 секунд.
    def get_total(self, key, calculator):
        cached = self.client.get(key)
        if cached is not None:
            self.hits += 1
            return float(cached), "cache"
        self.misses += 1
        value = calculator()
        self.client.setex(key, 60, str(value))
        return value, "db"


def cdn_headers():
    """Заголовки, которые ставят перед статикой тарифа на CDN."""
    return {
        "Cache-Control": "public, max-age=86400",
        "Content-Type": "image/svg+xml",
    }


def write_static():
    folder = os.path.join(BASE, "static", "tariffs")
    os.makedirs(folder, exist_ok=True)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="320" height="80">
<rect width="320" height="80" fill="#123"/>
<text x="16" y="48" fill="white" font-size="22">Тариф 100 Мбит/с</text>
</svg>
"""
    path = os.path.join(folder, "home100.svg")
    with open(path, "w", encoding="utf-8") as file:
        file.write(svg)
    versioned = os.path.join(folder, "home100.v1.svg")
    with open(versioned, "w", encoding="utf-8") as file:
        file.write(svg)
    note = os.path.join(BASE, "static", "cache-policy.json")
    with open(note, "w", encoding="utf-8") as file:
        json.dump(
            {
                "resource": "/static/tariffs/home100.v1.svg",
                "why_cdn": "картинка тарифа одинакова для всех абонентов и редко меняется",
                "cache_control": "public, max-age=86400",
                "versioning": "новое изображение публикуется как home100.v2.svg, старый URL не инвалидируют вручную",
            },
            file,
            ensure_ascii=False,
            indent=2,
        )
    return path
