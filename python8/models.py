"""Тарифы, которые создаёт фабрика."""

from dataclasses import dataclass, field


@dataclass
class Tariff:
    kind: str
    name: str
    base_fee: float
    subscribers: list[str] = field(default_factory=list)

    def title(self) -> str:
        return f"{self.kind}: {self.name} ({self.base_fee:.0f} руб.)"
