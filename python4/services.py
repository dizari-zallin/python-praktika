"""Бизнес-логика учёта грузов."""

from exceptions import CargoNotFoundError, ValidationError
from models import STATUSES, Cargo


class CargoService:
    """Операции над коллекцией грузов. Хранение передаётся снаружи."""

    def __init__(self, repository):
        self.repository = repository
        self.cargos = []

    # Читает коллекцию из хранилища и пишет факт загрузки в журнал.
    def load(self):
        self.cargos = self.repository.load()
        self.repository.write_log(f"загрузка, записей: {len(self.cargos)}")

    # Сохраняет текущий список. Резервную копию делает само хранилище.
    def save(self):
        self.repository.save(self.cargos)
        self.repository.write_log(f"сохранение JSON, записей: {len(self.cargos)}")

    def export_csv(self):
        self.repository.export_csv(self.cargos)
        self.repository.write_log(f"экспорт CSV, записей: {len(self.cargos)}")

    def import_csv(self):
        self.cargos = self.repository.import_csv()
        self.repository.write_log(f"импорт CSV, записей: {len(self.cargos)}")

    # Новый груз. Повтор номера запрещён до создания объекта.
    def add(self, number, sender, recipient, mass, status="принят"):
        if self.find(number) is not None:
            raise ValidationError("груз с таким номером уже существует")
        cargo = Cargo(number, sender, recipient, mass, status)
        self.cargos.append(cargo)
        self.repository.write_log(f"создан груз {cargo.number}")
        return cargo

    def find(self, number):
        number_lower = number.lower()
        for cargo in self.cargos:
            if cargo.number.lower() == number_lower:
                return cargo
        return None

    # Возвращает груз или поднимает исключение, если номера нет.
    def require(self, number):
        cargo = self.find(number)
        if cargo is None:
            raise CargoNotFoundError(f"груз «{number}» не найден")
        return cargo

    # Меняет статус. Отменённый и уже доставленный груз дальше не двигается.
    def change_status(self, number, status):
        cargo = self.require(number)
        if status not in STATUSES:
            raise ValidationError("недопустимый статус")
        if cargo.status == "отменён":
            raise ValidationError("нельзя изменить статус отменённого груза")
        if cargo.status == "доставлен" and status != "доставлен":
            raise ValidationError("доставленный груз нельзя вернуть в работу")
        cargo.status = status
        self.repository.write_log(f"статус {cargo.number} → {status}")
        return cargo

    def search(self, text):
        needle = text.lower()
        return [
            cargo
            for cargo in self.cargos
            if needle in cargo.number.lower()
            or needle in cargo.sender.lower()
            or needle in cargo.recipient.lower()
        ]

    def filter_by_status(self, status):
        return [cargo for cargo in self.cargos if cargo.status == status]

    def filter_by_mass(self, min_mass, max_mass):
        return [
            cargo
            for cargo in self.cargos
            if min_mass <= cargo.mass <= max_mass
        ]

    # Считает итоги одним проходом: сумма массы, счётчики статусов, самый тяжёлый груз.
    def statistics(self):
        total = len(self.cargos)
        mass_sum = 0
        by_status = {status: 0 for status in STATUSES}
        for cargo in self.cargos:
            mass_sum += cargo.mass
            by_status[cargo.status] += 1
        average = mass_sum / total if total else 0
        heaviest = None
        if self.cargos:
            heaviest = self.cargos[0]
            for cargo in self.cargos:
                if cargo.mass > heaviest.mass:
                    heaviest = cargo
        return {
            "count": total,
            "mass_sum": mass_sum,
            "average": average,
            "by_status": by_status,
            "heaviest": heaviest,
        }
