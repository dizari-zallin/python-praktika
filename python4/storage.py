"""Сохранение грузов в JSON и CSV. Слой хранения отделён от бизнес-логики."""

import csv
import json
import os
import shutil
from datetime import datetime

from exceptions import StorageError
from models import Cargo


class JsonRepository:
    """Репозиторий: загрузка и сохранение коллекции грузов."""

    def __init__(self, json_path, csv_path, backup_dir, log_path):
        self.json_path = json_path
        self.csv_path = csv_path
        self.backup_dir = backup_dir
        self.log_path = log_path

    # Если JSON ещё не создан, это не ошибка: программа стартует с пустым списком.
    def load(self):
        """Загружает грузы. Отсутствующий файл не считается ошибкой запуска."""
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                raw = json.load(file)
        except json.JSONDecodeError as exc:
            raise StorageError(f"JSON-файл повреждён: {exc}") from exc
        except OSError as exc:
            raise StorageError(f"не удалось прочитать файл: {exc}") from exc

        if not isinstance(raw, list):
            raise StorageError("JSON должен содержать список грузов")

        cargos = []
        for item in raw:
            cargos.append(Cargo.from_dict(item))
        return cargos

    # Перед перезаписью копирует старый JSON в backup, затем сериализует объекты через to_dict.
    def save(self, cargos):
        """Сохраняет грузы и делает резервную копию предыдущего файла."""
        folder = os.path.dirname(self.json_path)
        os.makedirs(folder, exist_ok=True)
        if os.path.exists(self.json_path):
            os.makedirs(self.backup_dir, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = os.path.join(self.backup_dir, f"data_{stamp}.json")
            shutil.copy2(self.json_path, backup)

        payload = [cargo.to_dict() for cargo in cargos]
        try:
            with open(self.json_path, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
        except OSError as exc:
            raise StorageError(f"не удалось сохранить JSON: {exc}") from exc

    # Та же коллекция в табличном виде: одна строка CSV — один груз.
    def export_csv(self, cargos):
        folder = os.path.dirname(self.csv_path)
        os.makedirs(folder, exist_ok=True)
        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["number", "sender", "recipient", "mass", "status"],
            )
            writer.writeheader()
            for cargo in cargos:
                writer.writerow(cargo.to_dict())

    # Обратное чтение CSV. Каждая строка снова собирается в Cargo через from_dict.
    def import_csv(self):
        if not os.path.exists(self.csv_path):
            raise StorageError("CSV-файл не найден")
        cargos = []
        with open(self.csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cargos.append(
                    Cargo.from_dict(
                        {
                            "number": row["number"],
                            "sender": row["sender"],
                            "recipient": row["recipient"],
                            "mass": float(row["mass"]),
                            "status": row["status"],
                        }
                    )
                )
        return cargos

    def write_log(self, message):
        folder = os.path.dirname(self.log_path)
        os.makedirs(folder, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as file:
            file.write(f"{stamp} {message}\n")

    def read_log(self):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8") as file:
            return [line.rstrip("\n") for line in file]
