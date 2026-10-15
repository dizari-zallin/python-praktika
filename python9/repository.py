"""Хранилище тарифов в памяти."""

from models import Tariff


class TariffRepository:
    def __init__(self):
        self._items: dict[int, Tariff] = {}
        self._next = 1

    def seed(self):
        self.add("Домашний 100", 100, 500, "Москва")
        self.add("Домашний 300", 300, 800, "Москва")
        self.add("Корпоративный 500", 500, 2500, "Казань")

    def add(self, name, speed, price, region) -> Tariff:
        item = Tariff(self._next, name, speed, price, region)
        self._items[item.id] = item
        self._next += 1
        return item

    def all(self) -> list[Tariff]:
        return list(self._items.values())

    def get(self, item_id: int) -> Tariff | None:
        return self._items.get(item_id)

    def update(self, item_id: int, **fields) -> Tariff | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None

    def by_speed(self, min_speed: int) -> list[Tariff]:
        return [item for item in self._items.values() if item.speed >= min_speed]
