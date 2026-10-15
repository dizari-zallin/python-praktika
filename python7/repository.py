"""Хранилище абонентов. Сервис зависит от абстракции, а не от файла."""

from typing import Protocol

from models import Subscriber


class SubscriberRepository(Protocol):
    def add(self, subscriber: Subscriber) -> None:
        ...

    def all(self) -> list[Subscriber]:
        ...

    def find(self, name: str) -> Subscriber | None:
        ...


class MemorySubscriberRepository:
    def __init__(self):
        self._items: list[Subscriber] = []

    def add(self, subscriber: Subscriber) -> None:
        self._items.append(subscriber)

    def all(self) -> list[Subscriber]:
        return list(self._items)

    def find(self, name: str) -> Subscriber | None:
        for item in self._items:
            if item.name.lower() == name.lower():
                return item
        return None
