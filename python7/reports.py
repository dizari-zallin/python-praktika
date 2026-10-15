"""Формирование отчёта вынесено из сервиса подключения (SRP)."""

from repository import SubscriberRepository


class TextReport:
    def __init__(self, repository: SubscriberRepository):
        self.repository = repository

    def render(self) -> str:
        lines = ["Абонент | Тариф | Месяцев | Блокировка"]
        for item in self.repository.all():
            blocked = "да" if item.blocked else "нет"
            lines.append(f"{item.name} | {item.tariff_code} | {item.months} | {blocked}")
        return "\n".join(lines)
