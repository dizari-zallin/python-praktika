"""Система абонентов для проверки тестами."""


class ProviderError(Exception):
    pass


class Provider:
    def __init__(self, tariffs=None):
        self.tariffs = tariffs or {
            "Домашний 100": 500,
            "Домашний 300": 800,
            "Корпоративный 500": 2500,
        }
        self.subscribers = {}

    def register(self, name, phone):
        if not name.strip() or not phone.strip():
            raise ProviderError("имя и телефон обязательны")
        if phone in self.subscribers:
            raise ProviderError("абонент уже зарегистрирован")
        self.subscribers[phone] = {
            "name": name,
            "phone": phone,
            "tariff": None,
            "balance": 0,
            "blocked": False,
        }
        return self.subscribers[phone]

    def connect(self, phone, tariff):
        person = self._get(phone)
        if tariff not in self.tariffs:
            raise ProviderError("тариф не найден")
        person["tariff"] = tariff
        return self.cost(phone)

    # Смена тарифа запрещена, пока абонент заблокирован из-за долга.
    def change_tariff(self, phone, tariff):
        person = self._get(phone)
        if person["blocked"]:
            raise ProviderError("абонент заблокирован")
        if person["tariff"] is None:
            raise ProviderError("тариф ещё не подключён")
        return self.connect(phone, tariff)

    def cost(self, phone):
        person = self._get(phone)
        if person["tariff"] is None:
            return 0
        return self.tariffs[person["tariff"]]

    # Списание абонентской платы. Отрицательный баланс блокирует абонента.
    def charge(self, phone):
        person = self._get(phone)
        amount = self.cost(phone)
        person["balance"] -= amount
        if person["balance"] < 0:
            person["blocked"] = True
        return person

    def pay(self, phone, amount):
        person = self._get(phone)
        if amount <= 0:
            raise ProviderError("сумма должна быть больше нуля")
        person["balance"] += amount
        if person["balance"] >= 0:
            person["blocked"] = False
        return person

    def _get(self, phone):
        if phone not in self.subscribers:
            raise ProviderError("абонент не найден")
        return self.subscribers[phone]
