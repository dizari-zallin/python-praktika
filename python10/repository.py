"""Хранилище тарифов в памяти. HTTP-слой его не создаёт сам."""


class TariffRepository:
    def __init__(self):
        self._items = {}
        self._next = 1

    def add(self, data: dict):
        item_id = self._next
        self._next += 1
        data = dict(data)
        data["id"] = item_id
        self._items[item_id] = data
        return data

    def all(self):
        return list(self._items.values())

    def get(self, item_id: int):
        return self._items.get(item_id)

    def update(self, item_id: int, data: dict, partial: bool):
        current = self._items.get(item_id)
        if current is None:
            return None
        if partial:
            current.update({key: value for key, value in data.items() if key != "id"})
        else:
            current.clear()
            current.update(data)
            current["id"] = item_id
        return current

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
