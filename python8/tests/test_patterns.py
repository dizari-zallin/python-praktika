import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from factory import TariffFactory
from models import Tariff
from observer import TariffSubject
from repository import MemoryTariffRepository
from service import TariffService
from strategies import BaseFeeStrategy, DiscountStrategy, ExtraServicesStrategy, PriceCalculator


class MemoryObserver:
    def __init__(self):
        self.messages = []

    def update(self, message: str) -> None:
        self.messages.append(message)


def test_factory_kinds():
    factory = TariffFactory()
    assert factory.create("home", "Дом").base_fee == 500
    assert factory.create("corp", "Офис").base_fee == 2500
    assert factory.create("mobile", "Мобайл").base_fee == 350


def test_strategy_corporate_discount_and_extras():
    tariff = Tariff("corp", "Офис", 2500)
    calculator = PriceCalculator(
        [BaseFeeStrategy(), DiscountStrategy({"corp": 0.1}), ExtraServicesStrategy(100, 2)]
    )
    assert calculator.total(tariff) == 2450


def test_repository_find():
    repo = MemoryTariffRepository()
    repo.add(Tariff("home", "Дом", 500))
    assert repo.find("дом").kind == "home"
    assert repo.find("нет") is None


def test_observer_on_fee_change():
    observer = MemoryObserver()
    subject = TariffSubject()
    subject.attach(observer)
    service = TariffService(MemoryTariffRepository(), subject)
    service.create("mobile", "Мобайл")
    service.change_fee("Мобайл", 400)
    assert len(observer.messages) == 2
    assert "400" in observer.messages[1]


def test_unknown_kind():
    try:
        TariffFactory().create("vip", "VIP")
        assert False
    except ValueError:
        assert True
