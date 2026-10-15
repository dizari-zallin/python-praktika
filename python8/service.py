"""Сборка фабрики, стратегий, репозитория и наблюдателя."""

from factory import TariffFactory
from models import Tariff
from observer import TariffSubject
from strategies import DiscountStrategy, ExtraServicesStrategy, PriceCalculator, BaseFeeStrategy


class TariffService:
    def __init__(self, repository, subject: TariffSubject):
        self.repository = repository
        self.factory = TariffFactory()
        self.subject = subject

    def create(self, kind: str, name: str) -> Tariff:
        tariff = self.factory.create(kind, name)
        self.repository.add(tariff)
        self.subject.notify(f"создан тариф «{name}» ({kind})")
        return tariff

    def quote(self, name: str, extra_count: int) -> float:
        tariff = self.repository.find(name)
        if tariff is None:
            raise ValueError("тариф не найден")
        calculator = PriceCalculator(
            [
                BaseFeeStrategy(),
                DiscountStrategy({"corp": 0.1, "home": 0.0, "mobile": 0.05}),
                ExtraServicesStrategy(100, extra_count),
            ]
        )
        return calculator.total(tariff)

    def change_fee(self, name: str, new_fee: float) -> None:
        tariff = self.repository.find(name)
        if tariff is None:
            raise ValueError("тариф не найден")
        tariff.base_fee = new_fee
        self.subject.notify(f"абонентская плата «{name}» изменена на {new_fee:.0f} руб.")
