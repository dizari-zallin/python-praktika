"""Стратегии абонентской платы, скидки и дополнительных услуг."""

from typing import Protocol

from models import Tariff


class FeeStrategy(Protocol):
    def amount(self, tariff: Tariff) -> float:
        ...


class BaseFeeStrategy:
    def amount(self, tariff: Tariff) -> float:
        return tariff.base_fee


class DiscountStrategy:
    def __init__(self, rates: dict[str, float]):
        self.rates = rates

    def amount(self, tariff: Tariff) -> float:
        rate = self.rates.get(tariff.kind, 0.0)
        return tariff.base_fee * rate


class ExtraServicesStrategy:
    def __init__(self, price_per_service: float, count: int):
        self.price_per_service = price_per_service
        self.count = count

    def amount(self, tariff: Tariff) -> float:
        return self.price_per_service * self.count


class PriceCalculator:
    """Складывает выбранные стратегии. Новая стратегия не требует правки калькулятора."""

    def __init__(self, strategies: list):
        self.strategies = strategies

    # Итог = базовая плата − скидка + дополнительные услуги. Новая стратегия добавляется в список.
    def total(self, tariff: Tariff) -> float:
        fee = 0.0
        discount = 0.0
        extra = 0.0
        for strategy in self.strategies:
            value = strategy.amount(tariff)
            if isinstance(strategy, DiscountStrategy):
                discount += value
            elif isinstance(strategy, ExtraServicesStrategy):
                extra += value
            else:
                fee += value
        return fee - discount + extra
