import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import API_KEY, create_app
from repository import TariffRepository
from service import TariffService


def client():
    service = TariffService(TariffRepository())
    service.create({"name": "Домашний 100", "speed": 100, "price": 500})
    service.create({"name": "Быстрый 300", "speed": 300, "price": 900})
    application = create_app(service)
    application.testing = True
    test_client = application.test_client()
    test_client.environ_base = {}
    return test_client


HEADERS = {"X-API-Key": API_KEY}


def test_list_ok():
    response = client().get("/tariffs", headers=HEADERS)
    assert response.status_code == 200
    assert response.get_json()["total"] == 2


def test_get_missing():
    response = client().get("/tariffs/99", headers=HEADERS)
    assert response.status_code == 404


def test_create():
    response = client().post("/tariffs", headers=HEADERS, json={
        "name": "Ночной", "speed": 50, "price": 300, "region": "Тула",
    })
    assert response.status_code == 201
    assert response.get_json()["id"] == 3


def test_create_invalid():
    response = client().post("/tariffs", headers=HEADERS, json={"name": "", "speed": 10, "price": 1})
    assert response.status_code == 400


def test_patch_price():
    response = client().patch("/tariffs/1", headers=HEADERS, json={"price": 450})
    assert response.status_code == 200
    assert response.get_json()["price"] == 450


def test_put_replace():
    response = client().put("/tariffs/1", headers=HEADERS, json={
        "name": "Обновлённый", "speed": 200, "price": 700, "region": "Москва",
    })
    assert response.status_code == 200
    assert response.get_json()["name"] == "Обновлённый"


def test_delete():
    api = client()
    response = api.delete("/tariffs/1", headers=HEADERS)
    assert response.status_code == 204
    assert api.get("/tariffs/1", headers=HEADERS).status_code == 404


def test_by_speed():
    response = client().get("/tariffs/by-speed?min_speed=200", headers=HEADERS)
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_sort_price():
    response = client().get("/tariffs?sort=price", headers=HEADERS)
    prices = [item["price"] for item in response.get_json()["items"]]
    assert prices == sorted(prices)


def test_unauthorized():
    response = client().get("/tariffs")
    assert response.status_code == 401


def test_filter_status():
    api = client()
    api.patch("/tariffs/2", headers=HEADERS, json={"status": "архив"})
    response = api.get("/tariffs?status=архив", headers=HEADERS)
    assert response.get_json()["total"] == 1
