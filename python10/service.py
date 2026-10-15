"""Бизнес-правила тарифа, отдельно от маршрутов Flask."""

STATUSES = {"активен", "архив"}


class TariffService:
    def __init__(self, repository):
        self.repository = repository

    def validate(self, data: dict, partial: bool = False):
        required = ["name", "speed", "price"]
        if not partial:
            missing = [key for key in required if key not in data]
            if missing:
                raise ValueError("не заполнены поля: " + ", ".join(missing))
        if "speed" in data and int(data["speed"]) <= 0:
            raise ValueError("скорость должна быть больше нуля")
        if "price" in data and float(data["price"]) < 0:
            raise ValueError("цена не может быть отрицательной")
        if "status" in data and data["status"] not in STATUSES:
            raise ValueError("статус: активен или архив")
        if "name" in data and not str(data["name"]).strip():
            raise ValueError("название не должно быть пустым")

    def create(self, data: dict):
        self.validate(data)
        payload = {
            "name": data["name"].strip(),
            "speed": int(data["speed"]),
            "price": float(data["price"]),
            "traffic": data.get("traffic", "безлимит"),
            "services": data.get("services") or [],
            "region": data.get("region", "Москва"),
            "status": data.get("status", "активен"),
        }
        return self.repository.add(payload)

    def list_tariffs(self, status=None, sort=None, min_speed=None, page=1, size=20):
        items = self.repository.all()
        if status:
            items = [item for item in items if item["status"] == status]
        if min_speed is not None:
            items = [item for item in items if item["speed"] >= int(min_speed)]
        if sort == "price":
            items = sorted(items, key=lambda item: item["price"])
        elif sort == "speed":
            items = sorted(items, key=lambda item: item["speed"], reverse=True)
        start = (page - 1) * size
        return items[start:start + size], len(items)

    def by_speed(self, min_speed: int):
        return [item for item in self.repository.all() if item["speed"] >= min_speed]
