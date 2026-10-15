"""
Лабораторная работа №3. Вариант 20.
Система обучения: объектная модель учебных материалов.
"""

from abc import ABC, abstractmethod
import sys

# Корректный вывод русских символов в консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")


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


def read_non_empty(prompt):
    """Считывает непустую строку."""
    while True:
        text = read_line(prompt)
        if text:
            return text
        print("Ошибка: значение не должно быть пустым.")


def parse_int(text):
    """Преобразует строку в int или возвращает None."""
    if text.startswith("-") and text[1:].isdigit():
        return -int(text[1:])
    if text.isdigit():
        return int(text)
    return None


def read_int(prompt):
    """Считывает целое число, в том числе отрицательное."""
    while True:
        value = parse_int(read_line(prompt))
        if value is not None:
            return value
        print("Ошибка: введите целое число.")


def clip(text, width):
    """Обрезает строку до ширины колонки таблицы."""
    text = str(text)
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


# ---------------------------------------------------------------------------
# Базовый класс предметной области (п. 4.1 методички)
# ---------------------------------------------------------------------------
class LearningMaterial(ABC):
    """Учебный материал. Общий интерфейс для лекции, практики и теста."""

    # Атрибут класса: общий счётчик созданных материалов
    total_created = 0

    def __init__(self, title, topic, difficulty):
        self.title = title
        self.topic = topic
        self._status = "запланирован"
        self.difficulty = difficulty
        LearningMaterial.total_created += 1

    @staticmethod
    def check_difficulty(value):
        """Проверяет сложность. Используется свойством difficulty."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("сложность должна быть целым числом от 1 до 5")
        if value < 1 or value > 5:
            raise ValueError("сложность должна быть целым числом от 1 до 5")

    @property
    def difficulty(self):
        """Защищённый атрибут: сложность занятия (инкапсуляция, п. 4.5)."""
        return self._difficulty

    @difficulty.setter
    def difficulty(self, value):
        LearningMaterial.check_difficulty(value)
        self._difficulty = value

    @property
    def status(self):
        """Статус можно только читать: меняется методами класса."""
        return self._status

    @property
    def kind(self):
        return "материал"

    def get_info(self):
        """Человекочитаемое описание объекта."""
        return (
            f"{self.kind}: «{self.title}», тема «{self.topic}», "
            f"сложность {self.difficulty}, {self.specific_text()}, "
            f"объём {self.evaluate_volume()} мин, статус: {self.status}"
        )

    def complete(self):
        """Отмечает занятие выполненным (изменение состояния)."""
        self._status = "проведён"

    def reset(self):
        """Возвращает занятие в запланированное состояние."""
        self._status = "запланирован"

    @abstractmethod
    def evaluate_volume(self):
        """Общий метод оценки объёма занятия (минуты)."""
        pass

    @abstractmethod
    def process(self):
        """Провести занятие. У каждого типа своя реализация (полиморфизм)."""
        pass

    @abstractmethod
    def specific_text(self):
        """Краткое описание индивидуального параметра типа."""
        pass

    def __str__(self):
        return self.get_info()

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title!r})"

    def __lt__(self, other):
        """Сравнение по объёму: нужно для сортировки (доп. задание)."""
        if not isinstance(other, LearningMaterial):
            return NotImplemented
        if self.evaluate_volume() != other.evaluate_volume():
            return self.evaluate_volume() < other.evaluate_volume()
        return self.title.lower() < other.title.lower()

    def __add__(self, other):
        """Сумма объёмов двух занятий (перегрузка оператора)."""
        if not isinstance(other, LearningMaterial):
            return NotImplemented
        return self.evaluate_volume() + other.evaluate_volume()


# Лекция добавляет число слайдов и своё действие «провести».
class Lecture(LearningMaterial):
    """Лекция. Индивидуальный параметр — длительность в минутах."""

    def __init__(self, title, topic, difficulty, duration):
        super().__init__(title, topic, difficulty)
        self.duration = duration

    @property
    def kind(self):
        return "Лекция"

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("длительность лекции должна быть целым числом больше 0")
        self._duration = value

    def evaluate_volume(self):
        # Для лекции объём совпадает с длительностью
        return self.duration

    def academic_hours(self):
        """Дополнительная характеристика: академические часы (45 мин)."""
        return round(self.duration / 45, 2)

    def process(self):
        print(
            f"Лекция «{self.title}» проводится {self.duration} мин "
            f"({self.academic_hours()} акад. ч)."
        )
        self.complete()
        print(f"Статус изменён: {self.status}.")

    def specific_text(self):
        return f"{self.duration} мин"


# Практика хранит число заданий и действие «выполнить».
class Practice(LearningMaterial):
    """Практическое занятие. Индивидуальный параметр — число заданий."""

    MINUTES_PER_TASK = 15

    def __init__(self, title, topic, difficulty, tasks_count):
        super().__init__(title, topic, difficulty)
        self.tasks_count = tasks_count

    @property
    def kind(self):
        return "Практика"

    @property
    def tasks_count(self):
        return self._tasks_count

    @tasks_count.setter
    def tasks_count(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("количество заданий должно быть целым числом больше 0")
        self._tasks_count = value

    def evaluate_volume(self):
        # Каждое задание оценивается как 15 минут работы
        return self.tasks_count * Practice.MINUTES_PER_TASK

    def process(self):
        print(
            f"Практика «{self.title}»: выполняется {self.tasks_count} заданий "
            f"(оценка объёма {self.evaluate_volume()} мин)."
        )
        self.complete()
        print(f"Статус изменён: {self.status}.")

    def specific_text(self):
        return f"{self.tasks_count} заданий"


# Тест хранит число вопросов и действие «пройти».
class Quiz(LearningMaterial):
    """Тест (дополнительный производный класс, п. 15 методички)."""

    MINUTES_PER_QUESTION = 2

    def __init__(self, title, topic, difficulty, questions_count):
        super().__init__(title, topic, difficulty)
        self.questions_count = questions_count

    @property
    def kind(self):
        return "Тест"

    @property
    def questions_count(self):
        return self._questions_count

    @questions_count.setter
    def questions_count(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("количество вопросов должно быть целым числом больше 0")
        self._questions_count = value

    def evaluate_volume(self):
        return self.questions_count * Quiz.MINUTES_PER_QUESTION

    def process(self):
        print(
            f"Тест «{self.title}»: {self.questions_count} вопросов "
            f"(на выполнение {self.evaluate_volume()} мин)."
        )
        self.complete()
        print(f"Статус изменён: {self.status}.")

    def specific_text(self):
        return f"{self.questions_count} вопросов"


# Курс держит список разных материалов и считает статистику по ним.
class Course:
    """
    Курс содержит учебные материалы.
    Композиция: Course HAS-A LearningMaterial (п. 4.8, п. 9 методички).
    """

    def __init__(self, name, teacher):
        self.name = name
        self.teacher = teacher
        self._materials = []

    def add(self, material):
        self._materials.append(material)

    def remove_at(self, index):
        return self._materials.pop(index)

    def get(self, index):
        return self._materials[index]

    def is_empty(self):
        return len(self._materials) == 0

    def process_all(self):
        """Полиморфная обработка коллекции разных типов (п. 4.7, п. 8)."""
        print("\nПолиморфный вызов process() для всех материалов:")
        for item in self._materials:
            item.process()

    def volumes(self):
        total = 0
        for item in self._materials:
            total += item.evaluate_volume()
        return total

    def find(self, topic="", kind="", min_difficulty=None):
        """Поиск по нескольким параметрам (доп. задание)."""
        result = []
        topic_lower = topic.lower()
        kind_lower = kind.lower()
        for item in self._materials:
            if topic_lower and topic_lower not in item.topic.lower():
                continue
            if kind_lower and kind_lower not in item.kind.lower():
                continue
            if min_difficulty is not None and item.difficulty < min_difficulty:
                continue
            result.append(item)
        return result

    def sorted_by_volume(self):
        """Сортировка за счёт перегрузки __lt__."""
        return sorted(self._materials)

    def count_by_kind(self):
        counts = {}
        for item in self._materials:
            counts[item.kind] = counts.get(item.kind, 0) + 1
        return counts

    def count_completed(self):
        done = 0
        for item in self._materials:
            if item.status == "проведён":
                done += 1
        return done

    def __iter__(self):
        """Собственный перебор материалов курса (доп. задание)."""
        return iter(self._materials)

    def __len__(self):
        return len(self._materials)

    def __str__(self):
        return (
            f"Курс «{self.name}», преподаватель {self.teacher}, "
            f"материалов: {len(self._materials)}"
        )


def read_difficulty():
    """Считывает сложность через ту же проверку, что и property."""
    while True:
        value = read_int("  Сложность (1-5): ")
        try:
            LearningMaterial.check_difficulty(value)
            return value
        except ValueError as exc:
            print(f"Ошибка: {exc}")


def read_positive_field(prompt, error_text):
    """Считывает целое число больше нуля."""
    while True:
        value = read_int(prompt)
        if value > 0:
            return value
        print(f"Ошибка: {error_text}")


# Создаёт лекцию и сразу проверяет поля.
def create_lecture():
    title = read_non_empty("  Название лекции: ")
    topic = read_non_empty("  Тема: ")
    difficulty = read_difficulty()
    duration = read_positive_field(
        "  Длительность, мин: ",
        "длительность должна быть больше нуля.",
    )
    return Lecture(title, topic, difficulty, duration)


# Создаёт практическую работу.
def create_practice():
    title = read_non_empty("  Название практики: ")
    topic = read_non_empty("  Тема: ")
    difficulty = read_difficulty()
    tasks = read_positive_field(
        "  Количество заданий: ",
        "количество заданий должно быть больше нуля.",
    )
    return Practice(title, topic, difficulty, tasks)


# Создаёт тест.
def create_quiz():
    title = read_non_empty("  Название теста: ")
    topic = read_non_empty("  Тема: ")
    difficulty = read_difficulty()
    questions = read_positive_field(
        "  Количество вопросов: ",
        "количество вопросов должно быть больше нуля.",
    )
    return Quiz(title, topic, difficulty, questions)


# Общая таблица: тип объекта виден рядом с названием.
def print_materials(materials, title="Список учебных материалов"):
    print(f"\n{title}:")
    if len(materials) == 0:
        print("Подходящих объектов нет.")
        return

    print(
        f"{'N':<4}{'Тип':<12}{'Название':<28}{'Тема':<16}"
        f"{'Сл.':<5}{'Параметр':<16}{'Объём':<8}{'Статус'}"
    )
    for index, item in enumerate(materials, start=1):
        print(
            f"{index:<4}"
            f"{clip(item.kind, 11):<12}"
            f"{clip(item.title, 27):<28}"
            f"{clip(item.topic, 15):<16}"
            f"{item.difficulty:<5}"
            f"{clip(item.specific_text(), 15):<16}"
            f"{item.evaluate_volume():<8}"
            f"{item.status}"
        )


# Пользователь выбирает объект по номеру строки.
def choose_index(course, prompt="Введите номер объекта: "):
    while True:
        value = read_int(prompt)
        if 1 <= value <= len(course):
            return value - 1
        print(f"Ошибка: номер должен быть от 1 до {len(course)}.")


def ensure_not_empty(course):
    if course.is_empty():
        print("Ошибка: сначала создайте хотя бы один объект.")
        return False
    return True


# Меню создания одного из трёх наследников.
def create_object(course):
    print("\nТип учебного материала:")
    print("  1. Лекция")
    print("  2. Практика")
    print("  3. Тест")
    choice = read_line("Выберите тип: ")

    if choice == "1":
        material = create_lecture()
    elif choice == "2":
        material = create_practice()
    elif choice == "3":
        material = create_quiz()
    else:
        print("Ошибка: выберите тип 1, 2 или 3.")
        return

    course.add(material)
    print("Объект создан.")
    print(material)


# Одно и то же место меню вызывает разное действие в зависимости от типа объекта.
def run_action(course):
    print("\nДействие:")
    print("  1. Провести выбранное занятие (process)")
    print("  2. Оценить объём выбранного занятия")
    print("  3. Провести все занятия (полиморфизм)")
    print("  4. Поиск по нескольким параметрам")
    print("  5. Сортировка по объёму")
    print("  6. Суммарный объём двух занятий (оператор +)")
    choice = read_line("Выберите действие: ")

    if choice == "1":
        print_materials(list(course))
        item = course.get(choose_index(course))
        print()
        item.process()

    elif choice == "2":
        print_materials(list(course))
        item = course.get(choose_index(course))
        print(f"\nОценка объёма «{item.title}»: {item.evaluate_volume()} мин")
        print(item.get_info())

    elif choice == "3":
        course.process_all()

    elif choice == "4":
        print("Пустое значение означает «любой».")
        topic = read_line("  Тема (фрагмент): ")
        kind = read_line("  Тип (Лекция/Практика/Тест): ")
        min_text = read_line("  Минимальная сложность (Enter — любая): ")
        min_difficulty = None
        if min_text:
            min_difficulty = parse_int(min_text)
            if min_difficulty is None:
                print("Ошибка: минимальная сложность должна быть целым числом.")
                return
        found = course.find(topic, kind, min_difficulty)
        print_materials(found, "Результат поиска")

    elif choice == "5":
        ordered = course.sorted_by_volume()
        print_materials(ordered, "Материалы по возрастанию объёма")

    elif choice == "6":
        if len(course) < 2:
            print("Ошибка: нужно минимум два объекта.")
            return
        print_materials(list(course))
        first = course.get(choose_index(course, "Номер первого объекта: "))
        second = course.get(choose_index(course, "Номер второго объекта: "))
        total = first + second
        print(
            f"\n{first.kind} «{first.title}» + {second.kind} «{second.title}» "
            f"= {total} мин"
        )

    else:
        print("Ошибка: выберите пункт от 1 до 6.")


# Изменение идёт через свойства, поэтому проверка остаётся внутри класса.
def edit_object(course):
    print_materials(list(course))
    item = course.get(choose_index(course))
    print("\nТекущее состояние:")
    print(item)
    print("\nЧто изменить?")
    print("  1. Название")
    print("  2. Тема")
    print("  3. Сложность")
    print("  4. Индивидуальный параметр")
    print("  5. Сбросить статус в «запланирован»")
    choice = read_line("Выберите поле: ")

    if choice == "1":
        item.title = read_non_empty("Новое название: ")
    elif choice == "2":
        item.topic = read_non_empty("Новая тема: ")
    elif choice == "3":
        while True:
            value = read_int("Новая сложность (1-5): ")
            try:
                item.difficulty = value
                break
            except ValueError as exc:
                print(f"Ошибка: {exc}")
    elif choice == "4":
        change_specific_parameter(item)
    elif choice == "5":
        item.reset()
    else:
        print("Ошибка: выберите пункт от 1 до 5.")
        return

    print("Объект изменён.")
    print(item)


# У каждого типа своё дополнительное поле: слайды, задания или вопросы.
def change_specific_parameter(item):
    """Изменяет длительность, число заданий или число вопросов."""
    while True:
        try:
            if isinstance(item, Lecture):
                item.duration = read_int("Новая длительность, мин: ")
            elif isinstance(item, Practice):
                item.tasks_count = read_int("Новое количество заданий: ")
            elif isinstance(item, Quiz):
                item.questions_count = read_int("Новое количество вопросов: ")
            return
        except ValueError as exc:
            print(f"Ошибка: {exc}")


# Убирает выбранный материал из курса.
def delete_object(course):
    print_materials(list(course))
    index = choose_index(course)
    item = course.get(index)
    print("\nОбъект будет удалён:")
    print(item)
    confirm = read_line("Подтвердите удаление (да/нет): ")
    if confirm.lower() in ("да", "д", "yes", "y"):
        course.remove_at(index)
        print("Объект удалён.")
    else:
        print("Удаление отменено.")


# Сколько материалов каждого типа и какая средняя сложность.
def print_statistics(course):
    print("\n----- Статистика курса -----")
    print(course)
    print(f"Всего создано материалов за сессию: {LearningMaterial.total_created}")
    print(f"Сейчас в курсе: {len(course)}")
    if course.is_empty():
        return

    print("По типам:")
    for kind, count in course.count_by_kind().items():
        print(f"  {kind}: {count}")

    total_volume = course.volumes()
    done = course.count_completed()
    print(f"Суммарный объём занятий: {total_volume} мин")
    print(f"Проведено: {done}, запланировано: {len(course) - done}")

    hardest = course.get(0)
    for item in course:
        if item.difficulty > hardest.difficulty:
            hardest = item
        elif item.difficulty == hardest.difficulty and item.evaluate_volume() > hardest.evaluate_volume():
            hardest = item
    print(f"Самый сложный материал: {hardest.kind} «{hardest.title}» (сложность {hardest.difficulty})")

    ordered = course.sorted_by_volume()
    print(f"Наименьший объём: {ordered[0].kind} «{ordered[0].title}» — {ordered[0].evaluate_volume()} мин")
    print(f"Наибольший объём: {ordered[-1].kind} «{ordered[-1].title}» — {ordered[-1].evaluate_volume()} мин")


# Пункты системы обучения.
def print_menu():
    print()
    print("===== МЕНЮ =====")
    print()
    print("1. Создать объект")
    print("2. Показать объекты")
    print("3. Выполнить действие")
    print("4. Изменить объект")
    print("5. Удалить объект")
    print("6. Показать статистику")
    print("0. Выход")
    print()


# Один курс на всё время работы программы.
def main():
    print("Лабораторная работа №3. Вариант 20 — система обучения")
    print("Курс содержит учебные материалы (композиция Course HAS-A LearningMaterial).")
    print()
    name = read_non_empty("Название курса: ")
    teacher = read_non_empty("Преподаватель: ")
    course = Course(name, teacher)
    print(f"Создан объект курса: {course}")

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")

        # Создание лекции, практики или теста и добавление в курс.
        if choice == "1":
            create_object(course)
        # Таблица материалов и подробное описание каждого объекта.
        elif choice == "2":
            if ensure_not_empty(course):
                print_materials(list(course), "Все объекты курса")
                print("\nПодробно:")
                for item in course:
                    print(" -", item)
        # Полиморфные действия: process, объём, поиск, сортировка, оператор +.
        elif choice == "3":
            if ensure_not_empty(course):
                run_action(course)
        # Изменение полей объекта. Сложность проходит через property.
        elif choice == "4":
            if ensure_not_empty(course):
                edit_object(course)
        # Удаление материала из коллекции курса.
        elif choice == "5":
            if ensure_not_empty(course):
                delete_object(course)
        # Сводка по типам, объёму и самому сложному материалу.
        elif choice == "6":
            print_statistics(course)
        elif choice == "0":
            print("Работа программы завершена.")
            break
        else:
            print("Ошибка: выберите пункт меню от 0 до 6.")


if __name__ == "__main__":
    main()
