"""Узкие интерфейсы вместо одного «толстого» (ISP)."""

from typing import Protocol


class BlockNotifier(Protocol):
    def notify_blocked(self, name: str) -> None:
        ...


class PaymentNotifier(Protocol):
    def notify_payment(self, name: str, amount: float) -> None:
        ...


class ConsoleNotifier:
    def notify_blocked(self, name: str) -> None:
        print(f"Уведомление: абонент {name} заблокирован")

    def notify_payment(self, name: str, amount: float) -> None:
        print(f"Уведомление: с абонента {name} начислено {amount:.0f} руб.")
