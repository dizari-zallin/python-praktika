"""
Лабораторная работа №2. Вариант 20.
Обработка заказов доставки.
"""

import sys

# Корректный вывод русских символов в консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    # При запуске из файла/конвейера читаем ввод как UTF-8
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")

# Кортеж допустимых статусов (значения не должны меняться в ходе работы)
STATUSES = ("оформлен", "в пути", "доставлен", "отменён")


def read_line(prompt):
    """Читает строку. В неинтерактивном режиме повторяет ввод в консоль."""
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


def read_positive_int(prompt):
    """Считывает целое положительное число и повторяет запрос при ошибке."""
    while True:
        text = read_line(prompt)
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Ошибка: введите целое положительное число.")


def is_non_negative_number(text):
    """Проверяет, что строка содержит неотрицательное вещественное число."""
    text = text.replace(",", ".", 1)
    if text.count(".") > 1:
        return False

    parts = text.split(".")
    if len(parts) == 1:
        return parts[0].isdigit()

    left = parts[0]
    right = parts[1]
    if left == "":
        left = "0"
    if right == "":
        return False
    return left.isdigit() and right.isdigit()


def read_non_negative_float(prompt):
    """Считывает неотрицательное вещественное число."""
    while True:
        text = read_line(prompt)
        if is_non_negative_number(text):
            return float(text.replace(",", ".", 1))
        print("Ошибка: введите число не меньше нуля (например, 12.5).")


def read_positive_float(prompt):
    """Считывает положительное вещественное число."""
    while True:
        value = read_non_negative_float(prompt)
        if value > 0:
            return value
        print("Ошибка: значение должно быть больше нуля.")


def read_non_empty(prompt):
    """Считывает непустую строку."""
    while True:
        text = read_line(prompt)
        if text:
            return text
        print("Ошибка: значение не должно быть пустым.")


# Проверяет, что номер заказа ещё не занят.
def number_exists(orders, number):
    """Проверяет, есть ли уже заказ с таким номером."""
    for order in orders:
        if order["number"].lower() == number.lower():
            return True
    return False


# Номер заказа должен быть новым.
def read_unique_number(orders, prompt):
    """Считывает уникальный номер заказа."""
    while True:
        number = read_non_empty(prompt)
        if number_exists(orders, number):
            print("Ошибка: заказ с таким номером уже существует.")
        else:
            return number


# Статус выбирается только из фиксированного списка.
def read_status():
    """Считывает статус доставки из кортежа допустимых значений."""
    print("Статус доставки:")
    for index, status in enumerate(STATUSES, start=1):
        print(f"  {index}. {status}")

    while True:
        text = read_line("Выберите статус (1-4): ")
        if text.isdigit() and 1 <= int(text) <= len(STATUSES):
            return STATUSES[int(text) - 1]
        print("Ошибка: выберите номер статуса от 1 до 4.")


# Собирает один заказ: номер, город, расстояние, стоимость и статус.
def input_order(orders):
    """Формирует словарь одного заказа по данным пользователя."""
    number = read_unique_number(orders, "  Номер заказа: ")
    city = read_non_empty("  Город доставки: ")
    distance = read_positive_float("  Расстояние, км: ")
    cost = read_non_negative_float("  Стоимость, руб.: ")
    status = read_status()
    return {
        "number": number,
        "city": city,
        "distance": distance,
        "cost": cost,
        "status": status,
    }


# Печатает заказы таблицей.
def print_orders(orders, title="Список заказов"):
    """Выводит коллекцию заказов в виде таблицы."""
    print(f"\n{title}:")
    if len(orders) == 0:
        print("Подходящих заказов нет.")
        return

    print(
        f"{'N':<4}{'Номер':<12}{'Город':<16}"
        f"{'Расст., км':<14}{'Стоимость':<14}{'Статус'}"
    )
    for index, order in enumerate(orders, start=1):
        print(
            f"{index:<4}{order['number']:<12}{order['city']:<16}"
            f"{order['distance']:<14.2f}{order['cost']:<14.2f}{order['status']}"
        )


# Линейный поиск заказов выбранного города.
def find_by_city(orders, city):
    """Ищет заказы по городу (list comprehension)."""
    city_lower = city.lower()
    return [
        order
        for order in orders
        if order["city"].lower() == city_lower
    ]


# Поиск одного заказа по номеру.
def find_by_number(orders, number):
    """Ищет заказ по номеру. Возвращает словарь или None."""
    number_lower = number.lower()
    for order in orders:
        if order["number"].lower() == number_lower:
            return order
    return None


# Оставляет заказы короче или длиннее заданного порога.
def filter_by_distance(orders, limit, mode):
    """Фильтрует заказы по расстоянию (list comprehension)."""
    if mode == "max":
        return [
            order
            for order in orders
            if order["distance"] <= limit
        ]
    return [
        order
        for order in orders
        if order["distance"] >= limit
    ]


# Два условия сразу: расстояние и статус.
def filter_by_distance_and_status(orders, limit, status):
    """Дополнительная фильтрация сразу по двум критериям."""
    return [
        order
        for order in orders
        if order["distance"] <= limit and order["status"] == status
    ]


# Новый список, исходный порядок заказов не меняется.
def sort_by_distance(orders, reverse=False):
    """Возвращает новый список, отсортированный по расстоянию."""
    return sorted(orders, key=lambda order: order["distance"], reverse=reverse)


# Сначала по километрам, при равенстве — по стоимости.
def sort_by_distance_and_cost(orders):
    """Сортировка по двум параметрам: расстояние, затем стоимость."""
    return sorted(orders, key=lambda order: (order["distance"], order["cost"]))


# Средняя стоимость заказа.
def calculate_average_cost(orders):
    """Средняя стоимость. Считается циклом, как требуется методичкой."""
    total = 0
    for order in orders:
        total += order["cost"]
    return total / len(orders)


# Суммарный километраж всех заказов.
def calculate_total_distance(orders):
    """Общий километраж всех заказов."""
    total = 0
    for order in orders:
        total += order["distance"]
    return total


# Самый маленький и самый большой заказ по выбранному полю.
def find_extreme_orders(orders, field):
    """Находит заказы с минимальным и максимальным значением поля."""
    min_order = orders[0]
    max_order = orders[0]
    for order in orders:
        if order[field] < min_order[field]:
            min_order = order
        if order[field] > max_order[field]:
            max_order = order
    return min_order, max_order


# Города без повторов.
def unique_cities(orders):
    """Возвращает множество уникальных городов доставки."""
    cities = [order["city"] for order in orders]
    return set(cities)


# Статусы, которые реально встретились в заказах.
def unique_statuses(orders):
    """Возвращает множество уникальных статусов."""
    return {order["status"] for order in orders}


# Словарь: город и список его заказов.
def group_by_city(orders):
    """Группирует заказы по городу в словарь списков."""
    groups = {}
    for order in orders:
        city = order["city"]
        if city not in groups:
            groups[city] = []
        groups[city].append(order)
    return groups


# Добавляет один или несколько заказов в общий список.
def add_orders(orders):
    """Добавляет один или несколько заказов в список."""
    count = read_positive_int("Сколько заказов добавить: ")
    for i in range(count):
        print(f"\nЗаказ {i + 1} из {count}:")
        order = input_order(orders)
        orders.append(order)
        print("Заказ добавлен.")


# Поиск по городу или по номеру.
def search_orders(orders):
    """Поиск заказов по городу или по номеру."""
    print("\nПоиск:")
    print("1. По городу")
    print("2. По номеру заказа")
    choice = read_line("Выберите вид поиска: ")

    if choice == "1":
        city = read_non_empty("Введите город: ")
        found = find_by_city(orders, city)
        print_orders(found, f"Заказы в городе {city}")
    elif choice == "2":
        number = read_non_empty("Введите номер заказа: ")
        found = find_by_number(orders, number)
        if found is None:
            print("Заказ с таким номером не найден.")
        else:
            print_orders([found], f"Заказ {number}")
    else:
        print("Ошибка: выберите 1 или 2.")


# Фильтры по расстоянию и статусу.
def filter_orders(orders):
    """Фильтрация по расстоянию или по двум критериям."""
    print("\nФильтрация:")
    print("1. По расстоянию")
    print("2. По расстоянию и статусу")
    choice = read_line("Выберите вид фильтрации: ")

    if choice == "1":
        print("1. Расстояние не больше заданного")
        print("2. Расстояние не меньше заданного")
        mode_choice = read_line("Выберите условие: ")
        if mode_choice == "1":
            limit = read_non_negative_float("Введите максимальное расстояние, км: ")
            found = filter_by_distance(orders, limit, "max")
            print_orders(found, f"Заказы с расстоянием <= {limit:.2f} км")
        elif mode_choice == "2":
            limit = read_non_negative_float("Введите минимальное расстояние, км: ")
            found = filter_by_distance(orders, limit, "min")
            print_orders(found, f"Заказы с расстоянием >= {limit:.2f} км")
        else:
            print("Ошибка: выберите 1 или 2.")
    elif choice == "2":
        limit = read_non_negative_float("Введите максимальное расстояние, км: ")
        status = read_status()
        found = filter_by_distance_and_status(orders, limit, status)
        print_orders(
            found,
            f"Заказы со статусом «{status}» и расстоянием <= {limit:.2f} км",
        )
    else:
        print("Ошибка: выберите 1 или 2.")


# Сортировки. Результат — новый список.
def sort_orders(orders):
    """Сортировка коллекции без изменения исходного списка."""
    print("\nСортировка:")
    print("1. По расстоянию (по возрастанию)")
    print("2. По расстоянию (по убыванию)")
    print("3. По расстоянию и стоимости")
    choice = read_line("Выберите вид сортировки: ")

    if choice == "1":
        print_orders(sort_by_distance(orders), "Заказы по возрастанию расстояния")
    elif choice == "2":
        print_orders(
            sort_by_distance(orders, reverse=True),
            "Заказы по убыванию расстояния",
        )
    elif choice == "3":
        print_orders(
            sort_by_distance_and_cost(orders),
            "Заказы по расстоянию, затем по стоимости",
        )
    else:
        print("Ошибка: выберите пункт от 1 до 3.")


# Сводка: средняя стоимость, километраж и крайние заказы.
def print_statistics(orders):
    """Выводит статистические показатели по заказам."""
    count = len(orders)
    average_cost = calculate_average_cost(orders)
    total_distance = calculate_total_distance(orders)
    average_distance = total_distance / count
    cheapest, expensive = find_extreme_orders(orders, "cost")
    nearest, farthest = find_extreme_orders(orders, "distance")

    print("\n----- Статистика -----")
    print(f"Количество заказов: {count}")
    print(f"Средняя стоимость: {average_cost:.2f} руб.")
    print(f"Общий километраж: {total_distance:.2f} км")
    print(f"Среднее расстояние: {average_distance:.2f} км")
    print(
        f"Самый дешёвый заказ: {cheapest['number']} "
        f"({cheapest['cost']:.2f} руб., {cheapest['city']})"
    )
    print(
        f"Самый дорогой заказ: {expensive['number']} "
        f"({expensive['cost']:.2f} руб., {expensive['city']})"
    )
    print(
        f"Ближайший заказ: {nearest['number']} "
        f"({nearest['distance']:.2f} км)"
    )
    print(
        f"Самый дальний заказ: {farthest['number']} "
        f"({farthest['distance']:.2f} км)"
    )

    print("\nКоличество заказов по статусам:")
    for status in STATUSES:
        status_count = 0
        for order in orders:
            if order["status"] == status:
                status_count += 1
        print(f"  {status}: {status_count}")


# Множества уникальных городов и статусов.
def print_unique_values(orders):
    """Выводит уникальные города и статусы."""
    cities = unique_cities(orders)
    statuses = unique_statuses(orders)

    print("\n----- Уникальные значения -----")
    print(f"Города доставки ({len(cities)}):")
    for city in sorted(cities):
        print(f"  {city}")

    print(f"\nСтатусы в текущем наборе ({len(statuses)}):")
    for status in sorted(statuses):
        print(f"  {status}")


# Меняет поля найденного заказа.
def edit_order(orders):
    """Изменяет выбранные поля существующего заказа."""
    number = read_non_empty("Введите номер заказа для изменения: ")
    order = find_by_number(orders, number)
    if order is None:
        print("Заказ с таким номером не найден.")
        return

    print_orders([order], "Текущие данные заказа")
    print("\nЧто изменить?")
    print("1. Город")
    print("2. Расстояние")
    print("3. Стоимость")
    print("4. Статус")
    choice = read_line("Выберите поле: ")

    if choice == "1":
        order["city"] = read_non_empty("Новый город: ")
    elif choice == "2":
        order["distance"] = read_positive_float("Новое расстояние, км: ")
    elif choice == "3":
        order["cost"] = read_non_negative_float("Новая стоимость, руб.: ")
    elif choice == "4":
        order["status"] = read_status()
    else:
        print("Ошибка: выберите пункт от 1 до 4.")
        return

    print("Заказ обновлён.")
    print_orders([order], "Обновлённые данные")


# Удаляет заказ по номеру.
def delete_order(orders):
    """Удаляет заказ по номеру."""
    number = read_non_empty("Введите номер заказа для удаления: ")
    order = find_by_number(orders, number)
    if order is None:
        print("Заказ с таким номером не найден.")
        return

    print_orders([order], "Заказ будет удалён")
    confirm = read_line("Подтвердите удаление (да/нет): ")
    if confirm.lower() in ("да", "д", "yes", "y"):
        orders.remove(order)
        print("Заказ удалён.")
    else:
        print("Удаление отменено.")


# Печатает заказы, сгруппированные по городам.
def print_groups(orders):
    """Выводит группировку заказов по городам."""
    groups = group_by_city(orders)
    print("\n----- Группировка по городу -----")
    for city, city_orders in groups.items():
        city_distance = calculate_total_distance(city_orders)
        city_cost = 0
        for order in city_orders:
            city_cost += order["cost"]
        print(f"\n{city}: заказов {len(city_orders)}, "
              f"километраж {city_distance:.2f} км, "
              f"сумма {city_cost:.2f} руб.")
        print_orders(city_orders, f"Заказы города {city}")


# Действия со списком недоступны, пока нет ни одного заказа.
def ensure_not_empty(orders):
    """Проверяет, что коллекция уже содержит данные."""
    if len(orders) == 0:
        print("Ошибка: сначала добавьте хотя бы один заказ.")
        return False
    return True


# Пункты работы со списком заказов.
def print_menu():
    print()
    print("===== МЕНЮ =====")
    print("1. Добавить объект")
    print("2. Показать объекты")
    print("3. Найти объект")
    print("4. Фильтрация")
    print("5. Сортировка")
    print("6. Статистика")
    print("7. Уникальные значения")
    print("8. Изменить объект")
    print("9. Удалить объект")
    print("10. Группировка по городу")
    print("0. Выход")
    print()


# Общий список заказов живёт всё время работы меню.
def main():
    # Основная коллекция: список словарей
    orders = []

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")

        # Добавление одного или нескольких заказов в список словарей.
        if choice == "1":
            add_orders(orders)
        # Таблица всех введённых заказов.
        elif choice == "2":
            if ensure_not_empty(orders):
                print_orders(orders, "Все введённые заказы")
        # Поиск по городу или по номеру.
        elif choice == "3":
            if ensure_not_empty(orders):
                search_orders(orders)
        # Отбор по расстоянию или сразу по расстоянию и статусу.
        elif choice == "4":
            if ensure_not_empty(orders):
                filter_orders(orders)
        # Сортировка выдаёт новый список и не меняет исходный.
        elif choice == "5":
            if ensure_not_empty(orders):
                sort_orders(orders)
        # Средняя стоимость, километраж и крайние заказы.
        elif choice == "6":
            if ensure_not_empty(orders):
                print_statistics(orders)
        # Множества уникальных городов и статусов.
        elif choice == "7":
            if ensure_not_empty(orders):
                print_unique_values(orders)
        # Изменение полей уже существующего заказа.
        elif choice == "8":
            if ensure_not_empty(orders):
                edit_order(orders)
        # Удаление заказа по номеру после подтверждения.
        elif choice == "9":
            if ensure_not_empty(orders):
                delete_order(orders)
        # Сводка заказов, сгруппированных по городу.
        elif choice == "10":
            if ensure_not_empty(orders):
                print_groups(orders)
        elif choice == "0":
            print("Работа программы завершена.")
            break
        else:
            print("Ошибка: выберите пункт меню от 0 до 10.")


if __name__ == "__main__":
    main()
