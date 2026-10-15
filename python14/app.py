"""
Лабораторная работа №14. Вариант 20.
REST API тарифов на FastAPI.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


class TariffIn(BaseModel):
    name: str = Field(min_length=1)
    speed: int = Field(gt=0)
    price: float = Field(ge=0)
    traffic: str = "безлимит"
    services: list[str] = []
    region: str = "Москва"
    status: str = "активен"


class Tariff(TariffIn):
    id: int


class TariffPatch(BaseModel):
    name: str | None = None
    speed: int | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, ge=0)
    traffic: str | None = None
    services: list[str] | None = None
    region: str | None = None
    status: str | None = None


def create_app():
    app = FastAPI(title="Тарифы провайдера")
    items: dict[int, dict] = {}
    seq = {"n": 1}

    def add(data: dict) -> dict:
        item = dict(data)
        item["id"] = seq["n"]
        seq["n"] += 1
        items[item["id"]] = item
        return item

    add({"name": "Домашний 100", "speed": 100, "price": 500, "traffic": "безлимит",
         "services": ["антивирус"], "region": "Москва", "status": "активен"})
    add({"name": "Домашний 300", "speed": 300, "price": 800, "traffic": "безлимит",
         "services": ["ТВ"], "region": "Казань", "status": "активен"})
    add({"name": "Корпоративный 500", "speed": 500, "price": 2500, "traffic": "гарантия",
         "services": ["белый IP"], "region": "Москва", "status": "активен"})

    @app.get("/tariffs")
    def list_tariffs(
        status: str | None = None,
        region: str | None = None,
        sort: str | None = None,
    ):
        result = list(items.values())
        if status:
            result = [item for item in result if item["status"] == status]
        if region:
            result = [item for item in result if item["region"] == region]
        if sort == "price":
            result = sorted(result, key=lambda item: item["price"])
        elif sort == "speed":
            result = sorted(result, key=lambda item: item["speed"], reverse=True)
        return result

    # Адрес объявлен раньше /tariffs/{id}, чтобы «by-speed» не приняли за номер.
    @app.get("/tariffs/by-speed")
    def by_speed(min_speed: int = Query(gt=0)):
        return [item for item in items.values() if item["speed"] >= min_speed]

    @app.get("/tariffs/{item_id}")
    def get_tariff(item_id: int):
        item = items.get(item_id)
        if item is None:
            raise HTTPException(404, "тариф не найден")
        return item

    # Pydantic уже проверил типы. Здесь остаётся только допустимый статус.
    @app.post("/tariffs", status_code=201)
    def create_tariff(payload: TariffIn):
        if payload.status not in {"активен", "архив"}:
            raise HTTPException(400, "статус: активен или архив")
        return add(payload.model_dump())

    @app.put("/tariffs/{item_id}")
    def replace_tariff(item_id: int, payload: TariffIn):
        if item_id not in items:
            raise HTTPException(404, "тариф не найден")
        saved = payload.model_dump()
        saved["id"] = item_id
        items[item_id] = saved
        return saved

    @app.patch("/tariffs/{item_id}")
    def patch_tariff(item_id: int, payload: TariffPatch):
        item = items.get(item_id)
        if item is None:
            raise HTTPException(404, "тариф не найден")
        changes = payload.model_dump(exclude_unset=True)
        item.update(changes)
        return item

    @app.delete("/tariffs/{item_id}", status_code=204)
    def delete_tariff(item_id: int):
        if item_id not in items:
            raise HTTPException(404, "тариф не найден")
        del items[item_id]

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5014)
