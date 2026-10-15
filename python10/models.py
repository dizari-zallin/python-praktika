"""Тариф как ресурс REST API."""

from dataclasses import dataclass, field, asdict


@dataclass
class Tariff:
    id: int
    name: str
    speed: int
    price: float
    traffic: str
    services: list[str] = field(default_factory=list)
    region: str = "Москва"
    status: str = "активен"

    def to_dict(self):
        return asdict(self)
