"""Функции высшего порядка и обработка коллекции грузов."""

from functools import reduce


def apply_to_each(items, operation):
    """Функция высшего порядка: применяет operation к каждому элементу."""
    return [operation(item) for item in items]


def select_where(items, predicate):
    """Функция высшего порядка: оставляет элементы, для которых predicate истинен."""
    return [item for item in items if predicate(item)]


# Оставляет грузы со статусом «доставлен». filter возвращает итератор, list материализует его.
def delivered(cargos):
    """Фильтрация доставленных грузов."""
    return list(filter(lambda cargo: cargo.status == "доставлен", cargos))


# map применяет функцию к каждому грузу и здесь забирает только номер.
def numbers_of(cargos):
    """Получение номеров через map."""
    return list(map(lambda cargo: cargo.number, cargos))


def sort_by_mass(cargos, reverse=False):
    return sorted(cargos, key=lambda cargo: cargo.mass, reverse=reverse)


# reduce складывает стоимости слева направо в одно число.
def total_cost(cargos):
    """Общая стоимость доставки через reduce."""
    if not cargos:
        return 0.0
    return reduce(lambda acc, cargo: acc + cargo.cost, cargos, 0.0)


# True, если хотя бы один груз тяжелее порога. Дальше коллекцию можно не смотреть.
def has_heavy(cargos, limit):
    """Есть ли грузы тяжелее заданной массы."""
    return any(cargo.mass > limit for cargo in cargos)


def all_have_cost(cargos):
    return all(cargo.cost > 0 for cargo in cargos)


def costs_by_number(cargos):
    """Dictionary comprehension: номер → стоимость."""
    return {cargo.number: cargo.cost for cargo in cargos}


def unique_statuses(cargos):
    return {cargo.status for cargo in cargos}


def heavy_numbers(cargos, limit):
    """List comprehension."""
    return [cargo.number for cargo in cargos if cargo.mass >= limit]
