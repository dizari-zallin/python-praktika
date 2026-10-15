"""Тесты бизнес-логики после рефакторинга."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from billing import CorporateStrategy, HomeStrategy, MobileStrategy, StrategyRegistry
from notifier import ConsoleNotifier
from repository import MemorySubscriberRepository
from service import SubscriberService


class SilentNotifier:
    def notify_blocked(self, name: str) -> None:
        pass

    def notify_payment(self, name: str, amount: float) -> None:
        pass


def make_service():
    repository = MemorySubscriberRepository()
    registry = StrategyRegistry([HomeStrategy(), CorporateStrategy(), MobileStrategy()])
    notifier = SilentNotifier()
    return SubscriberService(repository, registry, notifier, notifier), repository


def test_connect_home():
    service, _ = make_service()
    assert service.connect("Иванов", "home", 2) == 1000


def test_corporate_discount():
    service, _ = make_service()
    assert service.connect("Офис", "corp", 1) == 2250


def test_change_tariff():
    service, _ = make_service()
    service.connect("Петрова", "mobile", 2)
    assert service.change_tariff("Петрова", "home") == 1000


def test_blocked_payment_is_zero():
    service, _ = make_service()
    service.connect("Сидоров", "home", 3)
    service.block("Сидоров")
    assert service.payment("Сидоров") == 0


def test_unknown_tariff():
    service, _ = make_service()
    try:
        service.connect("Орлов", "vip", 1)
        assert False
    except ValueError:
        assert True


def test_duplicate_rejected():
    service, _ = make_service()
    service.connect("Иванов", "home", 1)
    try:
        service.connect("Иванов", "mobile", 1)
        assert False
    except ValueError:
        assert True
