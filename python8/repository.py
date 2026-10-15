"""Интерфейс репозитория и две реализации: память и JSON-файл."""

import json
import os

from models import Tariff


class MemoryTariffRepository:
    def __init__(self):
        self._items: list[Tariff] = []

    def add(self, tariff: Tariff) -> None:
        self._items.append(tariff)

    def all(self) -> list[Tariff]:
        return list(self._items)

    def find(self, name: str) -> Tariff | None:
        for item in self._items:
            if item.name.lower() == name.lower():
                return item
        return None


class JsonTariffRepository:
    def __init__(self, path: str):
        self.path = path
        self._items: list[Tariff] = []
        self.load()

    def add(self, tariff: Tariff) -> None:
        self._items.append(tariff)
        self.save()

    def all(self) -> list[Tariff]:
        return list(self._items)

    def find(self, name: str) -> Tariff | None:
        for item in self._items:
            if item.name.lower() == name.lower():
                return item
        return None

    def save(self) -> None:
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        payload = [
            {"kind": item.kind, "name": item.name, "base_fee": item.base_fee}
            for item in self._items
        ]
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def load(self) -> None:
        if not os.path.exists(self.path):
            self._items = []
            return
        with open(self.path, "r", encoding="utf-8") as file:
            raw = json.load(file)
        self._items = [Tariff(item["kind"], item["name"], item["base_fee"]) for item in raw]
