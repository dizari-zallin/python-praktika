"""
Лабораторная работа №7. Вариант 20.
Интернет-провайдер после рефакторинга по SOLID.
"""

import sys

from billing import CorporateStrategy, HomeStrategy, MobileStrategy, StrategyRegistry
from notifier import ConsoleNotifier
from reports import TextReport
from repository import MemorySubscriberRepository
from service import SubscriberService

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


def read_positive_int(prompt):
    while True:
        text = read_line(prompt)
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Ошибка: введите целое положительное число.")


def build_service():
    repository = MemorySubscriberRepository()
    registry = StrategyRegistry([HomeStrategy(), CorporateStrategy(), MobileStrategy()])
    notifier = ConsoleNotifier()
    service = SubscriberService(repository, registry, notifier, notifier)
    return service, repository


def print_menu():
    print()
    print("===== Провайдер (SOLID) =====")
    print("1. Подключить клиента")
    print("2. Изменить тариф")
    print("3. Заблокировать")
    print("4. Рассчитать оплату")
    print("5. Отчёт")
    print("0. Выход")
    print("Тарифы: home, corp, mobile")
    print()


def main():
    service, repository = build_service()
    print("Зависимости собраны снаружи: репозиторий, стратегии, уведомления.")
    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            # Подключение: стратегия по коду тарифа считает сумму, репозиторий хранит абонента.
            if choice == "1":
                name = read_line("Имя клиента: ")
                code = read_line("Код тарифа: ")
                months = read_positive_int("Месяцев: ")
                amount = service.connect(name, code, months)
                print(f"Клиент подключён. Начислено {amount:.0f} руб.")
            # Смена тарифа пересчитывает оплату. Заблокированному абоненту сервис откажет.
            elif choice == "2":
                name = read_line("Имя клиента: ")
                code = read_line("Новый код тарифа: ")
                amount = service.change_tariff(name, code)
                print(f"Тариф изменён. Новая сумма {amount:.0f} руб.")
            # Блокировка отделена от расчёта: уведомитель только сообщает о событии.
            elif choice == "3":
                name = read_line("Имя клиента: ")
                service.block(name)
            elif choice == "4":
                name = read_line("Имя клиента: ")
                print(f"К оплате: {service.payment(name):.0f} руб.")
            elif choice == "5":
                print(TextReport(repository).render())
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: выберите пункт от 0 до 5.")
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            break


if __name__ == "__main__":
    main()
