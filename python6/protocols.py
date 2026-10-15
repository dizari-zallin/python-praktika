"""Протокол объекта, который умеет описывать себя."""

from typing import Protocol


class Describable(Protocol):
    def describe(self) -> str:
        ...


def print_describable(item: Describable) -> None:
    """Функция работает через Protocol, не требуя общего базового класса."""
    print(item.describe())
