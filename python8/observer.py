"""Наблюдатели узнают об изменении тарифа."""

from typing import Protocol


class TariffObserver(Protocol):
    def update(self, message: str) -> None:
        ...


class SubscriberNotifier:
    def __init__(self):
        self.messages: list[str] = []

    def update(self, message: str) -> None:
        self.messages.append(message)
        print("Наблюдатель:", message)


class TariffSubject:
    def __init__(self):
        self._observers: list = []

    def attach(self, observer) -> None:
        self._observers.append(observer)

    # Одно событие уходит всем подписчикам. Отправитель не знает, кто именно слушает.
    def notify(self, message: str) -> None:
        for observer in self._observers:
            observer.update(message)
