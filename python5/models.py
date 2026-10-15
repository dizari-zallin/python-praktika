"""Классы грузов для функциональной обработки."""


class Cargo:
    """Базовый груз."""

    def __init__(self, number, sender, recipient, mass, cost, status):
        self.number = number
        self.sender = sender
        self.recipient = recipient
        self.mass = float(mass)
        self.cost = float(cost)
        self.status = status

    def kind(self):
        return "груз"

    def describe(self):
        return (
            f"{self.number} [{self.kind()}] {self.sender} → {self.recipient}, "
            f"{self.mass:.1f} кг, {self.cost:.0f} руб., {self.status}"
        )


class StandardCargo(Cargo):
    """Обычная доставка."""

    def kind(self):
        return "обычный"


class ExpressCargo(Cargo):
    """Срочная доставка: стоимость выше за счёт коэффициента."""

    def __init__(self, number, sender, recipient, mass, cost, status, hours):
        super().__init__(number, sender, recipient, mass, cost, status)
        self.hours = int(hours)

    def kind(self):
        return "срочный"

    def describe(self):
        return super().describe() + f", срок {self.hours} ч"
