"""
Лабораторная работа №1. Вариант 20.
Анализ работы службы доставки.
"""

import random
import sys

# Корректный вывод русских символов в консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# Строка с клавиатуры. Если ввод идёт не с экрана, набранное дублируется в консоль.
def read_line(prompt):
    """Читает строку с клавиатуры. В неинтерактивном режиме повторяет ввод в консоль."""
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


# Спрашивает снова, пока не получит целое число больше нуля.
def read_positive_int(prompt):
    """Считывает целое положительное число и повторяет запрос при ошибке."""
    while True:
        text = read_line(prompt)
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Ошибка: введите целое положительное число.")


# Текст годится, только если это число больше нуля.
def is_positive_number(text):
    """Проверяет, что строка содержит положительное вещественное число."""
    text = text.replace(",", ".", 1)
    if text.count(".") > 1:
        return False

    parts = text.split(".")
    if len(parts) == 1:
        return parts[0].isdigit() and float(text) > 0

    left = parts[0]
    right = parts[1]
    if left == "":
        left = "0"
    if right == "":
        return False
    if left.isdigit() and right.isdigit():
        return float(left + "." + right) > 0
    return False


# То же для дробного расстояния или времени в минутах.
def read_positive_float(prompt):
    """Считывает положительное вещественное число и повторяет запрос при ошибке."""
    while True:
        text = read_line(prompt)
        if is_positive_number(text):
            return float(text.replace(",", ".", 1))
        print("Ошибка: введите положительное число (например, 12.5).")


# Среднее арифметическое. Пустой список не приводит к делению на ноль.
def calculate_average(values):
    """Возвращает среднее арифметическое списка чисел."""
    total = 0
    for value in values:
        total += value
    return total / len(values)


# Позиции самой быстрой и самой долгой доставки в текущем наборе.
def find_extreme_indices(values):
    """Возвращает индексы наименьшего и наибольшего значений."""
    min_index = 0
    max_index = 0
    for i in range(1, len(values)):
        if values[i] < values[min_index]:
            min_index = i
        if values[i] > values[max_index]:
            max_index = i
    return min_index, max_index


# Скорость в км/ч: километры делим на время, минуты переводим в часы.
def calculate_speed(distance, time_minutes):
    """Рассчитывает скорость доставки в км/ч."""
    time_hours = time_minutes / 60
    return distance / time_hours


# Сколько доставок длились дольше допустимого лимита.
def count_late_orders(times, time_limit):
    """Считает заказы, выполненные позже нормативного времени."""
    late_count = 0
    for time_value in times:
        if time_value > time_limit:
            late_count += 1
    return late_count


# Сумма километров по всем заказам набора.
def calculate_total_distance(distances):
    """Возвращает общий километраж всех заказов."""
    total = 0
    for distance in distances:
        total += distance
    return total


# Пользователь сам вводит пары «расстояние — время».
def input_orders_manually():
    """Запрашивает у пользователя данные о заказах."""
    count = read_positive_int("Введите количество заказов: ")
    distances = []
    times = []

    for i in range(count):
        print(f"\nЗаказ {i + 1}:")
        distance = read_positive_float("  Расстояние доставки, км: ")
        time_value = read_positive_float("  Время выполнения, мин: ")
        distances.append(distance)
        times.append(time_value)

    time_limit = read_positive_float("\nВведите нормативное время доставки, мин: ")
    return distances, times, time_limit


# Случайный набор того же вида, чтобы не набирать цифры руками.
def generate_orders():
    """Формирует набор заказов с помощью генератора случайных значений."""
    count = read_positive_int("Введите количество заказов для генерации: ")
    distances = []
    times = []

    print()
    for i in range(count):
        distance = round(random.uniform(3.0, 35.0), 1)
        time_value = round(random.uniform(20.0, 140.0), 1)
        distances.append(distance)
        times.append(time_value)
        print(f"Заказ {i + 1}: расстояние {distance:.1f} км, время {time_value:.1f} мин")

    time_limit = read_positive_float("\nВведите нормативное время доставки, мин: ")
    return distances, times, time_limit


# Таблица заказов до расчёта показателей.
def print_orders(distances, times):
    """Выводит исходные данные по каждому заказу."""
    print("\nИсходные данные по заказам:")
    print(f"{'№':<4}{'Расстояние, км':<18}{'Время, мин':<14}{'Скорость, км/ч'}")
    for i in range(len(distances)):
        speed = calculate_speed(distances[i], times[i])
        print(f"{i + 1:<4}{distances[i]:<18.2f}{times[i]:<14.2f}{speed:.2f}")


# Основные показатели варианта: среднее время, крайние доставки, скорость, опоздания.
def print_main_statistics(distances, times, time_limit):
    """Выводит показатели, требуемые индивидуальным заданием."""
    print_orders(distances, times)

    # Показатели индивидуального задания: среднее время, крайние заказы и общий путь.
    average_time = calculate_average(times)
    fastest_index, slowest_index = find_extreme_indices(times)
    total_distance = calculate_total_distance(distances)
    total_time = 0
    for time_value in times:
        total_time += time_value
    # Средняя скорость всего маршрута: общий путь делим на суммарное время.
    average_speed = calculate_speed(total_distance, total_time)
    late_count = count_late_orders(times, time_limit)

    print("\n----- Основная статистика -----")
    print(f"Количество заказов: {len(distances)}")
    print(f"Нормативное время: {time_limit:.2f} мин")
    print(f"Среднее время доставки: {average_time:.2f} мин")
    print(
        f"Самый быстрый заказ: №{fastest_index + 1} "
        f"({times[fastest_index]:.2f} мин, {distances[fastest_index]:.2f} км)"
    )
    print(
        f"Самый медленный заказ: №{slowest_index + 1} "
        f"({times[slowest_index]:.2f} мин, {distances[slowest_index]:.2f} км)"
    )
    print(f"Средняя скорость доставки: {average_speed:.2f} км/ч")
    print(f"Заказов позже нормативного времени: {late_count}")
    print(f"Общий километраж: {total_distance:.2f} км")


# Словесная оценка сервиса по доле опозданий.
def evaluate_quality(late_percent):
    """Возвращает текстовую оценку качества работы службы доставки."""
    if late_percent <= 10:
        return "высокая (почти все заказы в срок)"
    elif late_percent <= 25:
        return "средняя (есть небольшие опоздания)"
    elif late_percent <= 50:
        return "пониженная (значительная доля опозданий)"
    else:
        return "низкая (большинство заказов с опозданием)"


# Дополнительный разбор и сравнение с предыдущим набором.
def print_extra_analysis(distances, times, time_limit, history):
    """Выводит дополнительные статистические показатели."""
    speeds = []
    for i in range(len(distances)):
        speeds.append(calculate_speed(distances[i], times[i]))

    average_time = calculate_average(times)
    average_distance = calculate_average(distances)
    average_of_speeds = calculate_average(speeds)
    min_speed_index, max_speed_index = find_extreme_indices(speeds)
    total_distance = calculate_total_distance(distances)
    late_count = count_late_orders(times, time_limit)
    late_percent = late_count / len(times) * 100

    faster_than_average = 0
    for time_value in times:
        if time_value < average_time:
            faster_than_average += 1

    total_time = 0
    for time_value in times:
        total_time += time_value

    print("\n----- Дополнительный анализ -----")
    print(f"Среднее расстояние: {average_distance:.2f} км")
    print(f"Суммарное время всех доставок: {total_time:.2f} мин")
    print(f"Минимальная скорость: {speeds[min_speed_index]:.2f} км/ч (заказ №{min_speed_index + 1})")
    print(f"Максимальная скорость: {speeds[max_speed_index]:.2f} км/ч (заказ №{max_speed_index + 1})")
    print(f"Средняя скорость по отдельным заказам: {average_of_speeds:.2f} км/ч")
    print(f"Заказов быстрее среднего времени: {faster_than_average}")
    print(f"Доля опозданий: {late_percent:.1f}%")
    print(f"Оценка качества работы: {evaluate_quality(late_percent)}")
    min_time_index, max_time_index = find_extreme_indices(times)
    print(f"Разброс времени доставки: {times[max_time_index] - times[min_time_index]:.2f} мин")

    records = []
    for item in history:
        records.append(item)
    records.append(make_history_record(distances, times, time_limit))

    if len(records) > 1:
        print(f"\nЗа текущую сессию обработано наборов данных: {len(records)}")
        print("Сравнение наборов:")
        print(f"{'Набор':<8}{'Заказов':<10}{'Ср. время':<14}{'Ср. скорость':<16}{'Километраж':<14}{'Опозданий'}")
        for i in range(len(records)):
            item = records[i]
            print(
                f"{i + 1:<8}{item[0]:<10}{item[1]:<14.2f}"
                f"{item[2]:<16.2f}{item[3]:<14.2f}{item[4]}"
            )


# Короткая запись набора, чтобы следующий запуск можно было сравнить с этим.
def make_history_record(distances, times, time_limit):
    """Формирует краткую запись о наборе данных для сравнения."""
    total_distance = calculate_total_distance(distances)
    total_time = 0
    for time_value in times:
        total_time += time_value
    average_time = calculate_average(times)
    average_speed = calculate_speed(total_distance, total_time)
    late_count = count_late_orders(times, time_limit)
    return (len(distances), average_time, average_speed, total_distance, late_count)


# Пункты меню: ввод, генерация, статистика, сброс и выход.
def print_menu():
    print()
    print("===== Анализ работы службы доставки =====")
    print()
    print("1. Ввести данные вручную")
    print("2. Сгенерировать данные случайным образом")
    print("3. Показать статистику")
    print("4. Выполнить дополнительный анализ")
    print("5. Начать новый набор данных")
    print("6. Выход")
    print()


# Цикл меню. Текущий набор и предыдущий хранятся отдельно, чтобы их сравнивать.
def main():
    distances = []
    times = []
    time_limit = 0
    datasets_count = 0
    history = []

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")

        # Ручной ввод. Если набор уже был, его краткие итоги сохраняются для сравнения.
        if choice == "1":
            if len(distances) > 0:
                history.append(make_history_record(distances, times, time_limit))
                print("Предыдущий набор сохранён для сравнения.")
            distances, times, time_limit = input_orders_manually()
            datasets_count += 1
            print("Данные успешно сохранены.")

        # Случайная генерация заказов. Предыдущий набор тоже остаётся в истории.
        elif choice == "2":
            if len(distances) > 0:
                history.append(make_history_record(distances, times, time_limit))
                print("Предыдущий набор сохранён для сравнения.")
            distances, times, time_limit = generate_orders()
            datasets_count += 1
            print("Случайные данные успешно сохранены.")

        # Основная статистика по варианту: среднее время, крайние заказы, скорость, опоздания, километраж.
        elif choice == "3":
            if len(distances) == 0:
                print("Ошибка: сначала введите или сгенерируйте данные.")
            else:
                print_main_statistics(distances, times, time_limit)

        # Дополнительный анализ: доли, оценка качества и сравнение нескольких наборов.
        elif choice == "4":
            if len(distances) == 0:
                print("Ошибка: сначала введите или сгенерируйте данные.")
            else:
                print_extra_analysis(distances, times, time_limit, history)

        # Сброс текущего набора, чтобы ввести следующий без перезапуска программы.
        elif choice == "5":
            if len(distances) > 0:
                history.append(make_history_record(distances, times, time_limit))
                print(f"Текущий набор сохранён. Всего обработано наборов: {datasets_count}")
                distances = []
                times = []
                time_limit = 0
                print("Можно ввести или сгенерировать новый набор заказов.")
            else:
                print("Текущий набор пуст. Сначала введите данные.")

        # Завершение цикла меню.
        elif choice == "6":
            print("Работа программы завершена.")
            break

        else:
            print("Ошибка: выберите пункт меню от 1 до 6.")


if __name__ == "__main__":
    main()
