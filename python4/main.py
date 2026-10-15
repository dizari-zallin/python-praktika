"""
Лабораторная работа №4. Вариант 20.
Система управления грузами: модули, исключения, JSON и CSV.
"""

import os
import sys

from exceptions import CargoError, CargoNotFoundError, StorageError, ValidationError
from models import STATUSES
from services import CargoService
from storage import JsonRepository

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# Чтение строки. При запуске из файла ввод повторяется на экране, чтобы был виден диалог.
def read_line(prompt):
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


# Пустую строку не принимает и спрашивает ещё раз.
def read_non_empty(prompt):
    while True:
        text = read_line(prompt)
        if text:
            return text
        print("Ошибка: значение не должно быть пустым.")


# Масса: число больше нуля, запятую можно писать вместо точки.
def read_positive_float(prompt):
    while True:
        text = read_line(prompt).replace(",", ".", 1)
        try:
            value = float(text)
        except ValueError:
            print("Ошибка: необходимо ввести число.")
            continue
        if value <= 0:
            print("Ошибка: масса должна быть больше нуля.")
            continue
        return value


# Таблица грузов. Пустой результат сообщает отдельно, без ошибки.
def print_cargos(cargos, title="Список грузов"):
    print(f"\n{title}:")
    if not cargos:
        print("Подходящих грузов нет.")
        return
    print(f"{'N':<4}{'Номер':<12}{'Отправитель':<18}{'Получатель':<18}{'Масса':<10}{'Статус'}")
    for index, cargo in enumerate(cargos, start=1):
        print(
            f"{index:<4}{cargo.number:<12}{cargo.sender:<18}"
            f"{cargo.recipient:<18}{cargo.mass:<10.1f}{cargo.status}"
        )


# Статус выбирается номером из фиксированного кортежа, а не произвольной строкой.
def read_status():
    print("Статус:")
    for index, status in enumerate(STATUSES, start=1):
        print(f"  {index}. {status}")
    while True:
        text = read_line("Выберите статус (1-4): ")
        if text.isdigit() and 1 <= int(text) <= len(STATUSES):
            return STATUSES[int(text) - 1]
        print("Ошибка: выберите номер статуса от 1 до 4.")


def create_cargo(service):
    # try/except/else/finally: ошибка данных не роняет программу, finally отмечает конец операции.
    try:
        number = read_non_empty("  Номер груза: ")
        sender = read_non_empty("  Отправитель: ")
        recipient = read_non_empty("  Получатель: ")
        mass = read_positive_float("  Масса, кг: ")
        status = read_status()
        cargo = service.add(number, sender, recipient, mass, status)
    except CargoError as exc:
        print(f"Ошибка: {exc}")
        return
    else:
        print("Груз создан.")
        print(cargo)
    finally:
        print("Операция создания завершена.")


# Смена статуса. Несуществующий номер даёт CargoNotFoundError.
def change_status(service):
    number = read_non_empty("Номер груза: ")
    status = read_status()
    try:
        cargo = service.change_status(number, status)
    except CargoNotFoundError as exc:
        print(f"Исключение CargoNotFoundError: {exc}")
    except ValidationError as exc:
        print(f"Ошибка: {exc}")
    else:
        print("Статус изменён.")
        print(cargo)


# Поиск по фрагменту номера, отправителя или получателя.
def search_cargo(service):
    text = read_non_empty("Фрагмент номера, отправителя или получателя: ")
    print_cargos(service.search(text), f"Поиск «{text}»")


# Фильтр либо по статусу, либо по диапазону массы.
def filter_cargos(service):
    print("1. По статусу")
    print("2. По массе")
    choice = read_line("Выберите фильтр: ")
    if choice == "1":
        status = read_status()
        print_cargos(service.filter_by_status(status), f"Статус «{status}»")
    elif choice == "2":
        min_mass = read_positive_float("Минимальная масса, кг: ")
        max_mass = read_positive_float("Максимальная масса, кг: ")
        if max_mass < min_mass:
            print("Ошибка: максимум не может быть меньше минимума.")
            return
        print_cargos(
            service.filter_by_mass(min_mass, max_mass),
            f"Масса от {min_mass:.1f} до {max_mass:.1f} кг",
        )
    else:
        print("Ошибка: выберите 1 или 2.")


# Сводка: количество, общая и средняя масса, разбивка по статусам, самый тяжёлый груз.
def show_statistics(service):
    stats = service.statistics()
    print("\n----- Статистика -----")
    print(f"Количество грузов: {stats['count']}")
    print(f"Общая масса: {stats['mass_sum']:.1f} кг")
    print(f"Средняя масса: {stats['average']:.1f} кг")
    print("По статусам:")
    for status, count in stats["by_status"].items():
        print(f"  {status}: {count}")
    if stats["heaviest"] is not None:
        heavy = stats["heaviest"]
        print(f"Самый тяжёлый груз: {heavy.number} ({heavy.mass:.1f} кг)")


# Последние строки журнала операций.
def show_log(service):
    lines = service.repository.read_log()
    print("\n----- Журнал операций -----")
    if not lines:
        print("Журнал пуст.")
        return
    for line in lines[-12:]:
        print(line)


def print_menu():
    print()
    print("===== Система управления грузами =====")
    print("1. Создать груз")
    print("2. Показать все грузы")
    print("3. Изменить статус")
    print("4. Найти груз")
    print("5. Фильтрация")
    print("6. Статистика")
    print("7. Сохранить JSON")
    print("8. Загрузить JSON")
    print("9. Экспортировать CSV")
    print("10. Импортировать CSV")
    print("11. Журнал операций")
    print("0. Выход")
    print()


def main():
    repository = JsonRepository(
        json_path=os.path.join(DATA_DIR, "data.json"),
        csv_path=os.path.join(DATA_DIR, "data.csv"),
        backup_dir=os.path.join(DATA_DIR, "backup"),
        log_path=os.path.join(DATA_DIR, "operations.log"),
    )
    service = CargoService(repository)
    try:
        service.load()
        print(f"Загружено грузов из JSON: {len(service.cargos)}")
    except StorageError as exc:
        print(f"Ошибка хранилища: {exc}")
        print("Работа продолжается с пустым списком.")
        service.cargos = []

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            # Новый груз остаётся в памяти, пока его отдельно не сохранят в JSON.
            if choice == "1":
                create_cargo(service)
            elif choice == "2":
                print_cargos(service.cargos, "Все грузы")
            elif choice == "3":
                change_status(service)
            elif choice == "4":
                search_cargo(service)
            elif choice == "5":
                filter_cargos(service)
            elif choice == "6":
                show_statistics(service)
            # Запись коллекции в JSON и резервная копия предыдущего файла.
            elif choice == "7":
                service.save()
                print(f"Данные сохранены: {repository.json_path}")
            # Повторное чтение JSON: так проверяется, что данные переживают перезапуск.
            elif choice == "8":
                service.load()
                print(f"Загружено записей: {len(service.cargos)}")
            elif choice == "9":
                service.export_csv()
                print(f"CSV создан: {repository.csv_path}")
            # CSV заменяет текущий список. Это второй источник данных помимо JSON.
            elif choice == "10":
                service.import_csv()
                print(f"Импортировано записей: {len(service.cargos)}")
            elif choice == "11":
                show_log(service)
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: выберите пункт меню от 0 до 11.")
        except CargoNotFoundError as exc:
            print(f"Исключение CargoNotFoundError: {exc}")
        except (ValidationError, StorageError, CargoError) as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            print("Ввод завершён.")
            break


if __name__ == "__main__":
    main()
