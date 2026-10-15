"""Сервис подключения. Зависимости передаются снаружи (DIP)."""

from billing import StrategyRegistry
from models import Subscriber
from notifier import BlockNotifier, PaymentNotifier
from repository import SubscriberRepository


class SubscriberService:
    def __init__(
        self,
        repository: SubscriberRepository,
        strategies: StrategyRegistry,
        payment_notifier: PaymentNotifier,
        block_notifier: BlockNotifier,
    ):
        self.repository = repository
        self.strategies = strategies
        self.payment_notifier = payment_notifier
        self.block_notifier = block_notifier

    # Создаёт абонента и считает оплату выбранной стратегией. Хранилище и уведомления приходят снаружи.
    def connect(self, name: str, tariff_code: str, months: int) -> float:
        if months <= 0:
            raise ValueError("число месяцев должно быть больше нуля")
        if self.repository.find(name) is not None:
            raise ValueError("абонент уже подключён")
        strategy = self.strategies.get(tariff_code)
        subscriber = Subscriber(name, tariff_code, False, months)
        self.repository.add(subscriber)
        amount = strategy.monthly_fee() * months
        self.payment_notifier.notify_payment(name, amount)
        return amount

    def change_tariff(self, name: str, tariff_code: str) -> float:
        subscriber = self.repository.find(name)
        if subscriber is None:
            raise ValueError("абонент не найден")
        if subscriber.blocked:
            raise ValueError("нельзя сменить тариф заблокированному абоненту")
        strategy = self.strategies.get(tariff_code)
        subscriber.tariff_code = tariff_code
        amount = strategy.monthly_fee() * subscriber.months
        self.payment_notifier.notify_payment(name, amount)
        return amount

    def block(self, name: str) -> None:
        subscriber = self.repository.find(name)
        if subscriber is None:
            raise ValueError("абонент не найден")
        subscriber.blocked = True
        self.block_notifier.notify_blocked(name)

    # Заблокированный абонент сейчас ничего не должен: оплата обнуляется.
    def payment(self, name: str) -> float:
        subscriber = self.repository.find(name)
        if subscriber is None:
            raise ValueError("абонент не найден")
        if subscriber.blocked:
            return 0.0
        strategy = self.strategies.get(subscriber.tariff_code)
        return strategy.monthly_fee() * subscriber.months
