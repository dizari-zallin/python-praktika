"""Генератор грузов выбранного статуса и собственный итератор."""


# Не строит список заранее: очередной подходящий груз появляется только при запросе.
def cargos_by_status(cargos, status):
    """Выдаёт грузы выбранного статуса по одному."""
    for cargo in cargos:
        if cargo.status == status:
            yield cargo


class CargoIterator:
    """Собственный итератор: обходит грузы тяжелее порога."""

    def __init__(self, cargos, min_mass):
        self._items = [cargo for cargo in cargos if cargo.mass >= min_mass]
        self._index = 0

    def __iter__(self):
        return self

    # Следующий тяжёлый груз. Когда индекс вышел за список, итератор сообщается через StopIteration.
    def __next__(self):
        if self._index >= len(self._items):
            raise StopIteration
        item = self._items[self._index]
        self._index += 1
        return item
