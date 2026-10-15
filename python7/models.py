"""Модели абонента после рефакторинга."""

from dataclasses import dataclass


@dataclass
class Subscriber:
    name: str
    tariff_code: str
    blocked: bool = False
    months: int = 1
