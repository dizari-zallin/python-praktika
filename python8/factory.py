"""Фабрика семейства тарифов."""

from models import Tariff


class TariffFactory:
    def create(self, kind: str, name: str) -> Tariff:
        fees = {"home": 500.0, "corp": 2500.0, "mobile": 350.0}
        if kind not in fees:
            raise ValueError("неизвестный вид тарифа")
        return Tariff(kind, name, fees[kind])
