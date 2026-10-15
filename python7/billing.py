"""Стратегии расчёта оплаты. Новая стратегия не меняет сервис (OCP)."""

from typing import Protocol


class PaymentStrategy(Protocol):
    code: str

    def monthly_fee(self) -> float:
        ...


class HomeStrategy:
    code = "home"

    def monthly_fee(self) -> float:
        return 500.0


# Корпоративный тариф: базовая плата со скидкой 10 процентов.
class CorporateStrategy:
    code = "corp"

    def monthly_fee(self) -> float:
        return 2500.0 * 0.9


class MobileStrategy:
    code = "mobile"

    def monthly_fee(self) -> float:
        return 350.0


class StrategyRegistry:
    def __init__(self, strategies: list[PaymentStrategy]):
        self._items = {item.code: item for item in strategies}

    def get(self, code: str) -> PaymentStrategy:
        if code not in self._items:
            raise ValueError(f"неизвестный тариф: {code}")
        return self._items[code]

    def register(self, strategy: PaymentStrategy) -> None:
        self._items[strategy.code] = strategy
