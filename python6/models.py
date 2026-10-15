"""Модели абонента, тарифа и подключения."""

from dataclasses import dataclass, field
from enum import Enum


class ConnectionStatus(Enum):
    ACTIVE = "активно"
    SUSPENDED = "приостановлено"
    DISABLED = "отключено"


@dataclass
class Entity:
    """Базовый класс предметной области."""

    id: int
    name: str


@dataclass
class Tariff(Entity):
    speed_mbps: int
    monthly_fee: float
    extra_service_fee: float = 0.0

    def describe(self) -> str:
        return (
            f"Тариф #{self.id} «{self.name}»: {self.speed_mbps} Мбит/с, "
            f"{self.monthly_fee:.0f} руб./мес"
        )


@dataclass
class Subscriber(Entity):
    phone: str
    balance: float = 0.0

    def describe(self) -> str:
        return f"Абонент #{self.id} {self.name}, тел. {self.phone}, баланс {self.balance:.0f} руб."


@dataclass
class Connection(Entity):
    subscriber_id: int
    tariff_id: int
    status: ConnectionStatus = ConnectionStatus.ACTIVE
    extras: list[str] = field(default_factory=list)

    def describe(self) -> str:
        extra = ", ".join(self.extras) if self.extras else "нет"
        return (
            f"Подключение #{self.id} «{self.name}»: абонент {self.subscriber_id}, "
            f"тариф {self.tariff_id}, {self.status.value}, услуги: {extra}"
        )
