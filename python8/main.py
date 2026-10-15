"""
Лабораторная работа №8. Вариант 20.
Паттерны: Factory, Strategy, Repository, Observer.
"""

import os
import sys

from naive import create_tariff, month_price
from observer import SubscriberNotifier, TariffSubject
from repository import MemoryTariffRepository
from service import TariffService

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))


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
        if text.isdigit():
            return int(text)
        print("Ошибка: введите целое неотрицательное число.")


def read_float(prompt):
    while True:
        text = read_line(prompt).replace(",", ".", 1)
        try:
            value = float(text)
        except ValueError:
            print("Ошибка: введите число.")
            continue
        if value <= 0:
            print("Ошибка: плата должна быть больше нуля.")
            continue
        return value


def print_menu():
    print()
    print("===== Тарифы провайдера =====")
    print("1. Показать наивный расчёт")
    print("2. Создать тариф (Factory)")
    print("3. Рассчитать стоимость (Strategy)")
    print("4. Изменить абонентскую плату (Observer)")
    print("5. Показать тарифы (Repository)")
    print("0. Выход")
    print("Виды: home, corp, mobile")
    print()


def main():
    subject = TariffSubject()
    subject.attach(SubscriberNotifier())
    service = TariffService(MemoryTariffRepository(), subject)
    print("Репозиторий в памяти. Наблюдатель подключён.")

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            # Наивный расчёт на if. Новый вид тарифа здесь требует правки этой же функции.
            if choice == "1":
                raw = create_tariff("corp", "Старый корпоративный")
                print("Наивная ветка if:", raw)
                print("Цена с 2 услугами:", month_price(raw, 2))
                print("Новый вид тарифа в наивной версии требует правки функции create_tariff.")
            # Фабрика сама выбирает базовую плату по виду тарифа.
            elif choice == "2":
                kind = read_line("Вид тарифа: ")
                name = read_line("Название: ")
                tariff = service.create(kind, name)
                print("Создан", tariff.title())
            # Стратегии отдельно считают абонплату, скидку и дополнительные услуги.
            elif choice == "3":
                name = read_line("Название тарифа: ")
                extras = read_int("Число дополнительных услуг: ")
                total = service.quote(name, extras)
                print(f"Итог: абонплата − скидка + услуги = {total:.0f} руб.")
            # Смена платы рассылается наблюдателям, тариф сам никого не печатает.
            elif choice == "4":
                name = read_line("Название тарифа: ")
                fee = read_float("Новая абонентская плата: ")
                service.change_fee(name, fee)
            elif choice == "5":
                items = service.repository.all()
                if not items:
                    print("Тарифов пока нет.")
                for item in items:
                    print(" -", item.title())
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
