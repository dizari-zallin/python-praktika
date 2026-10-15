"""Операции провайдера: стоимость и популярность тарифа."""

import inspect

from decorators import log_call, repeat, require_positive
from models import Connection, ConnectionStatus, Subscriber, Tariff


class ProviderError(Exception):
    pass


class NotFoundError(ProviderError):
    pass


class ProviderService:
    def __init__(self):
        self.subscribers: list[Subscriber] = []
        self.tariffs: list[Tariff] = []
        self.connections: list[Connection] = []
        self._next_id = 1

    def _new_id(self) -> int:
        value = self._next_id
        self._next_id += 1
        return value

    def add_subscriber(self, name: str, phone: str, balance: float) -> Subscriber:
        item = Subscriber(self._new_id(), name, phone, balance)
        self.subscribers.append(item)
        return item

    def add_tariff(self, name: str, speed: int, fee: float, extra_fee: float = 0) -> Tariff:
        item = Tariff(self._new_id(), name, speed, fee, extra_fee)
        self.tariffs.append(item)
        return item

    def add_connection(self, name: str, subscriber_id: int, tariff_id: int) -> Connection:
        self._require(self.subscribers, subscriber_id, "абонент")
        self._require(self.tariffs, tariff_id, "тариф")
        item = Connection(self._new_id(), name, subscriber_id, tariff_id)
        self.connections.append(item)
        return item

    def _require(self, items, item_id, title):
        for item in items:
            if item.id == item_id:
                return item
        raise NotFoundError(f"{title} #{item_id} не найден")

    def set_status(self, connection_id: int, status: ConnectionStatus) -> Connection:
        connection = self._require(self.connections, connection_id, "подключение")
        connection.status = status
        return connection

    @log_call
    @require_positive
    # Плата активного подключения за несколько месяцев плюс стоимость каждой доп. услуги.
    def service_cost(self, connection_id: int, months: int) -> float:
        """Стоимость услуг за несколько месяцев с учётом доп. услуг."""
        connection = self._require(self.connections, connection_id, "подключение")
        tariff = self._require(self.tariffs, connection.tariff_id, "тариф")
        extra = tariff.extra_service_fee * len(connection.extras)
        if connection.status != ConnectionStatus.ACTIVE:
            return 0.0
        return (tariff.monthly_fee + extra) * months

    # Самый частый тариф среди активных подключений.
    def most_popular_tariff(self) -> Tariff | None:
        if not self.tariffs:
            return None
        counts = {tariff.id: 0 for tariff in self.tariffs}
        for connection in self.connections:
            if connection.status == ConnectionStatus.ACTIVE:
                counts[connection.tariff_id] = counts.get(connection.tariff_id, 0) + 1
        best_id = max(counts, key=counts.get)
        return self._require(self.tariffs, best_id, "тариф")

    @repeat(2)
    def announce_popular(self) -> str:
        tariff = self.most_popular_tariff()
        if tariff is None:
            return "тарифов нет"
        return tariff.name

    def inspect_object(self, obj) -> None:
        print(f"type: {type(obj).__name__}")
        print(f"isinstance Entity: {isinstance(obj, __import__('models').Entity)}")
        print("dir (фрагмент):", ", ".join(name for name in dir(obj) if not name.startswith("_")))
        print("hasattr name:", hasattr(obj, "name"))
        print("getattr name:", getattr(obj, "name", None))
        print("сигнатура describe:", inspect.signature(obj.describe))
