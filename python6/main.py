"""
Лабораторная работа №6. Вариант 20.
Интернет-провайдер: dataclass, Enum, декораторы, контекст, Protocol.
"""

import sys

from context import OperationContext, timed_block
from models import ConnectionStatus
from protocols import print_describable
from services import NotFoundError, ProviderError, ProviderService

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")


def read_line(prompt):
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


def read_int(prompt):
    while True:
        text = read_line(prompt)
        if text.lstrip("-").isdigit():
            return int(text)
        print("Ошибка: введите целое число.")


def read_float(prompt):
    while True:
        text = read_line(prompt).replace(",", ".", 1)
        try:
            return float(text)
        except ValueError:
            print("Ошибка: введите число.")


def seed(service: ProviderService):
    home = service.add_tariff("Домашний 100", 100, 500, 100)
    corp = service.add_tariff("Корпоративный 500", 500, 2500, 300)
    mobile = service.add_tariff("Мобильный 50", 50, 350, 50)
    ivan = service.add_subscriber("Иванов", "79001112233", 1200)
    anna = service.add_subscriber("Петрова", "79004445566", 800)
    oleg = service.add_subscriber("Сидоров", "79007778899", 300)
    first = service.add_connection("кв. Иванова", ivan.id, home.id)
    second = service.add_connection("офис Петровой", anna.id, corp.id)
    third = service.add_connection("модем Сидорова", oleg.id, home.id)
    first.extras.append("статический IP")
    second.extras.append("белый IP")
    third.status = ConnectionStatus.SUSPENDED
    return first, second, third


def print_all(service: ProviderService):
    print("\nТарифы:")
    for item in service.tariffs:
        print_describable(item)
    print("\nАбоненты:")
    for item in service.subscribers:
        print_describable(item)
    print("\nПодключения:")
    for item in service.connections:
        print_describable(item)


def print_menu():
    print()
    print("===== Интернет-провайдер =====")
    print("1. Добавить тариф")
    print("2. Добавить абонента")
    print("3. Создать подключение")
    print("4. Вывести все объекты")
    print("5. Изменить статус подключения")
    print("6. Рассчитать стоимость услуг")
    print("7. Наиболее популярный тариф")
    print("8. Интроспекция объекта")
    print("9. Демонстрация декоратора с параметром")
    print("10. Демонстрация контекстного менеджера")
    print("0. Выход")
    print()


def main():
    service = ProviderService()
    with OperationContext("начальное наполнение"):
        seed(service)
    print("Созданы учебные абоненты, тарифы и подключения.")

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            # Новый тариф: скорость, абонентская плата и цена одной дополнительной услуги.
            if choice == "1":
                name = read_line("Название тарифа: ")
                speed = read_int("Скорость, Мбит/с: ")
                fee = read_float("Абонентская плата: ")
                extra = read_float("Плата за одну доп. услугу: ")
                item = service.add_tariff(name, speed, fee, extra)
                print("Добавлен", item.describe())
            elif choice == "2":
                name = read_line("ФИО: ")
                phone = read_line("Телефон: ")
                balance = read_float("Баланс: ")
                item = service.add_subscriber(name, phone, balance)
                print("Добавлен", item.describe())
            elif choice == "3":
                name = read_line("Название подключения: ")
                subscriber_id = read_int("ID абонента: ")
                tariff_id = read_int("ID тарифа: ")
                item = service.add_connection(name, subscriber_id, tariff_id)
                print("Создано", item.describe())
            elif choice == "4":
                print_all(service)
            elif choice == "5":
                connection_id = read_int("ID подключения: ")
                print("1. активно  2. приостановлено  3. отключено")
                status_choice = read_line("Статус: ")
                mapping = {
                    "1": ConnectionStatus.ACTIVE,
                    "2": ConnectionStatus.SUSPENDED,
                    "3": ConnectionStatus.DISABLED,
                }
                if status_choice not in mapping:
                    print("Ошибка: выберите 1, 2 или 3.")
                    continue
                item = service.set_status(connection_id, mapping[status_choice])
                print("Обновлено", item.describe())
            # Стоимость услуг. Декоратор require_positive не пропустит ноль месяцев.
            elif choice == "6":
                connection_id = read_int("ID подключения: ")
                months = read_int("Число месяцев: ")
                with timed_block("расчёт стоимости"):
                    cost = service.service_cost(connection_id, months)
                print(f"Стоимость услуг: {cost:.0f} руб.")
            elif choice == "7":
                tariff = service.most_popular_tariff()
                if tariff is None:
                    print("Тарифов нет.")
                else:
                    print("Самый популярный активный тариф:", tariff.describe())
            # Интроспекция: тип, атрибуты и сигнатура describe у живого объекта.
            elif choice == "8":
                if not service.connections:
                    print("Нет объектов.")
                    continue
                print("Интроспекция первого подключения:")
                service.inspect_object(service.connections[0])
            # Декоратор с параметром вызывает один и тот же расчёт два раза.
            elif choice == "9":
                print("Декоратор @repeat(2) вызывает расчёт популярности дважды.")
                print("Результат:", service.announce_popular())
            # Контекстный менеджер отмечает начало и конец блока, в том числе при ошибке.
            elif choice == "10":
                with OperationContext("проверка контекста"):
                    print("Внутри блока: считаем число подключений =", len(service.connections))
                print("Попытка некорректного расчёта внутри контекста:")
                try:
                    with OperationContext("некорректный расчёт"):
                        service.service_cost(service.connections[0].id, 0)
                except ValueError as exc:
                    print(f"Исключение перехвачено: {exc}")
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: выберите пункт меню от 0 до 10.")
        except NotFoundError as exc:
            print(f"Ошибка: {exc}")
        except ProviderError as exc:
            print(f"Ошибка: {exc}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            break


if __name__ == "__main__":
    main()
