"""Тариф интернет-провайдера."""

from dataclasses import dataclass, asdict


@dataclass
class Tariff:
    id: int
    name: str
    speed: int
    price: float
    region: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            speed=int(data["speed"]),
            price=float(data["price"]),
            region=str(data["region"]),
        )
