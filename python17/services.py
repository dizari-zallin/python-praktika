"""Бизнес-логика личного кабинета провайдера."""

from dataclasses import dataclass, field


@dataclass
class Account:
    name: str
    tariff: str
    fee: float
    services: list[str] = field(default_factory=list)
    payments: list[tuple[str, float]] = field(default_factory=list)
    blocked: bool = False


TARIFFS = {
    "Домашний 100": 500,
    "Домашний 300": 800,
    "Корпоративный 500": 2500,
}
SERVICE_PRICE = {"антивирус": 100, "ТВ": 250, "белый IP": 200}


class Cabinet:
    def __init__(self):
        self.accounts: dict[int, Account] = {}

    def register(self, user_id: int, name: str) -> str:
        self.accounts[user_id] = Account(name, "Домашний 100", TARIFFS["Домашний 100"], payments=[("аванс", 500)])
        return f"{name}, подключён тариф «Домашний 100»."

    def current_tariff(self, user_id: int) -> str:
        account = self._get(user_id)
        services = ", ".join(account.services) if account.services else "нет"
        state = "заблокирован" if account.blocked else "активен"
        return (
            f"Тариф «{account.tariff}», {account.fee:.0f} руб./мес, "
            f"услуги: {services}, состояние: {state}."
        )

    # Подключает услугу и прибавляет её цену к ежемесячной плате.
    def connect_service(self, user_id: int, service: str) -> str:
        account = self._get(user_id)
        if service not in SERVICE_PRICE:
            return "Такой услуги нет. Доступны: " + ", ".join(SERVICE_PRICE)
        if service in account.services:
            return f"Услуга «{service}» уже подключена."
        account.services.append(service)
        account.fee += SERVICE_PRICE[service]
        return f"Услуга «{service}» подключена. Новая плата {account.fee:.0f} руб."

    def history(self, user_id: int) -> str:
        account = self._get(user_id)
        if not account.payments:
            return "Платежей пока нет."
        lines = [f"{title}: {amount:.0f} руб." for title, amount in account.payments]
        return "История платежей:\n" + "\n".join(lines)

    # Меняет базовый тариф и сохраняет уже подключённые услуги. Должнику смена закрыта.
    def change_tariff(self, user_id: int, tariff: str) -> str:
        account = self._get(user_id)
        if account.blocked:
            return "Смена тарифа недоступна: есть задолженность, абонент заблокирован."
        if tariff not in TARIFFS:
            return "Тариф не найден. Доступны: " + ", ".join(TARIFFS)
        extra = sum(SERVICE_PRICE[name] for name in account.services)
        account.tariff = tariff
        account.fee = TARIFFS[tariff] + extra
        account.payments.append((f"смена на {tariff}", 0))
        return f"Тариф изменён на «{tariff}». К оплате {account.fee:.0f} руб."

    def pay(self, user_id: int, amount: float) -> str:
        account = self._get(user_id)
        account.payments.append(("оплата", amount))
        if amount >= account.fee:
            account.blocked = False
        return f"Платёж {amount:.0f} руб. принят."

    def _get(self, user_id: int) -> Account:
        if user_id not in self.accounts:
            raise KeyError("Сначала отправьте /start")
        return self.accounts[user_id]


cabinet = Cabinet()
