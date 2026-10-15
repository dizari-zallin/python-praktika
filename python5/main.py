"""
Лабораторная работа №5. Вариант 20.
Функциональная обработка грузов.
"""

import sys

from generators import CargoIterator, cargos_by_status
from models import ExpressCargo, StandardCargo
from operations import (
    all_have_cost,
    apply_to_each,
    costs_by_number,
    delivered,
    has_heavy,
    heavy_numbers,
    numbers_of,
    select_where,
    sort_by_mass,
    total_cost,
    unique_statuses,
)

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


def read_float(prompt):
    while True:
        text = read_line(prompt).replace(",", ".", 1)
        try:
            return float(text)
        except ValueError:
            print("Ошибка: введите число.")


def print_cargos(cargos, title):
    print(f"\n{title}:")
    if not cargos:
        print("Подходящих грузов нет.")
        return
    for cargo in cargos:
        print(" -", cargo.describe())


def sample_data():
    return [
        StandardCargo("G-101", "Озон", "Иванов", 12.5, 900, "доставлен"),
        ExpressCargo("G-102", "М.Видео", "Петрова", 4.2, 1500, "в пути", 6),
        StandardCargo("G-103", "Склад Юг", "Сидоров", 40.0, 2400, "принят"),
        ExpressCargo("G-104", "Озон", "Кузнецова", 2.1, 1100, "доставлен", 4),
        StandardCargo("G-105", "Ламода", "Орлов", 8.0, 700, "отменён"),
        ExpressCargo("G-106", "Склад Юг", "Иванов", 25.0, 3200, "доставлен", 12),
    ]


def show_lazy_difference(cargos):
    """Показывает, что генератор не строит список заранее."""
    print("\n----- Список и генератор -----")
    ready = [cargo.number for cargo in cargos if cargo.status == "доставлен"]
    print("Список номеров доставленных построен сразу:", ready)
    print("type(list) =", type(ready).__name__)

    lazy = cargos_by_status(cargos, "доставлен")
    print("Генератор создан, элементы ещё не вычислены. type =", type(lazy).__name__)
    print("Первый next():", next(lazy).number)
    print("Второй next():", next(lazy).number)
    print("Остаток генератора:", [cargo.number for cargo in lazy])


def print_menu():
    print()
    print("===== Обработка грузов =====")
    print("1. Показать все объекты")
    print("2. Отфильтровать доставленные")
    print("3. Получить номера")
    print("4. Отсортировать по массе")
    print("5. Общая стоимость доставки")
    print("6. Запустить генератор по статусу")
    print("7. Проверить наличие тяжёлых грузов")
    print("8. Собственный итератор")
    print("9. Сравнение списка и генератора")
    print("0. Выход")
    print()


def main():
    cargos = sample_data()
    print("Загружен учебный набор грузов:", len(cargos))
    print("Классы:", ", ".join(sorted({type(item).__name__ for item in cargos})))

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            # Исходная коллекция из двух наследников: обычный и срочный груз.
            if choice == "1":
                print_cargos(cargos, "Все грузы")
            # filter оставляет только доставленные.
            elif choice == "2":
                found = delivered(cargos)
                print_cargos(found, "Доставленные грузы (filter + lambda)")
            # map и функция высшего порядка дают одни и те же номера.
            elif choice == "3":
                print("Номера (map):", ", ".join(numbers_of(cargos)))
                described = apply_to_each(cargos, lambda cargo: cargo.number)
                print("Та же выборка через функцию высшего порядка:", ", ".join(described))
            # sorted с key не меняет исходный список.
            elif choice == "4":
                ordered = sort_by_mass(cargos)
                print_cargos(ordered, "По возрастанию массы (sorted + key)")
            # reduce сворачивает стоимости в одну сумму, any/all проверяют коллекцию целиком.
            elif choice == "5":
                print(f"Общая стоимость (reduce): {total_cost(cargos):.0f} руб.")
                print("Стоимости по номерам:", costs_by_number(cargos))
                print("Уникальные статусы:", ", ".join(sorted(unique_statuses(cargos))))
                print("У всех грузов стоимость > 0:", all_have_cost(cargos))
            # Генератор отдаёт грузы выбранного статуса по одному через yield.
            elif choice == "6":
                status = read_line("Статус (принят / в пути / доставлен / отменён): ")
                print(f"Генератор выдаёт грузы со статусом «{status}» по одному:")
                count = 0
                for cargo in cargos_by_status(cargos, status):
                    count += 1
                    print(f"  yield → {cargo.describe()}")
                if count == 0:
                    print("  генератор не выдал ни одного значения")
            # any отвечает, есть ли груз тяжелее порога.
            elif choice == "7":
                limit = read_float("Порог массы, кг: ")
                print(f"any(масса > {limit:.1f}): {has_heavy(cargos, limit)}")
                print("Номера не легче порога:", heavy_numbers(cargos, limit) or "нет")
                cheap = select_where(cargos, lambda cargo: cargo.cost < 1000)
                print_cargos(cheap, "Дополнительно: стоимость меньше 1000 (функция высшего порядка)")
            # Собственный итератор обходит только грузы не легче порога и заканчивается StopIteration.
            elif choice == "8":
                limit = read_float("Минимальная масса для итератора, кг: ")
                iterator = CargoIterator(cargos, limit)
                print("Обход собственным итератором:")
                try:
                    while True:
                        cargo = next(iterator)
                        print("  next →", cargo.describe())
                except StopIteration:
                    print("StopIteration: элементы закончились")
            # Список строится сразу, генератор выдаёт значение только на next().
            elif choice == "9":
                show_lazy_difference(cargos)
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: выберите пункт меню от 0 до 9.")
        except EOFError:
            print("Ввод завершён.")
            break
        except ValueError as exc:
            print(f"Ошибка данных: {exc}")


if __name__ == "__main__":
    main()
