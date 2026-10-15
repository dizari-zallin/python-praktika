"""Модель груза."""

from exceptions import ValidationError

STATUSES = ("принят", "в пути", "доставлен", "отменён")


class Cargo:
    """Груз логистической службы."""

    def __init__(self, number, sender, recipient, mass, status="принят"):
        self.number = number
        self.sender = sender
        self.recipient = recipient
        self.mass = mass
        self.status = status

    @staticmethod
    def _check_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"поле «{field_name}» не должно быть пустым")
        return value.strip()

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = self._check_text(value, "номер")

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = self._check_text(value, "отправитель")

    @property
    def recipient(self):
        return self._recipient

    @recipient.setter
    def recipient(self, value):
        self._recipient = self._check_text(value, "получатель")

    @property
    def mass(self):
        return self._mass

    # Масса только положительное число. Логическое True/False сюда не проходит.
    @mass.setter
    def mass(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValidationError("масса должна быть положительным числом")
        self._mass = float(value)

    @property
    def status(self):
        return self._status

    # Статус только из списка STATUSES, произвольная строка отклоняется.
    @status.setter
    def status(self, value):
        if value not in STATUSES:
            allowed = ", ".join(STATUSES)
            raise ValidationError(f"недопустимый статус. Доступны: {allowed}")
        self._status = value

    # Объект -> словарь. Так груз попадает в JSON.
    def to_dict(self):
        """Объект → словарь для JSON."""
        return {
            "number": self.number,
            "sender": self.sender,
            "recipient": self.recipient,
            "mass": self.mass,
            "status": self.status,
        }

    # Словарь -> объект. classmethod нужен, потому что экземпляра ещё нет.
    @classmethod
    def from_dict(cls, data):
        """Словарь → объект. classmethod обязателен по методичке."""
        return cls(
            number=data["number"],
            sender=data["sender"],
            recipient=data["recipient"],
            mass=data["mass"],
            status=data.get("status", "принят"),
        )

    def __str__(self):
        return (
            f"{self.number}: {self.sender} → {self.recipient}, "
            f"{self.mass:.1f} кг, {self.status}"
        )
