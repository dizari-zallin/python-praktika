import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from app import create_app


def api():
    return TestClient(create_app())


def test_list():
    response = api().get("/tariffs")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_by_speed():
    response = api().get("/tariffs/by-speed", params={"min_speed": 300})
    assert response.status_code == 200
    assert all(item["speed"] >= 300 for item in response.json())


def test_create_and_patch():
    client = api()
    created = client.post("/tariffs", json={
        "name": "Ночной", "speed": 50, "price": 300, "traffic": "ночь",
        "services": [], "region": "Тула", "status": "активен",
    })
    assert created.status_code == 201
    item_id = created.json()["id"]
    patched = client.patch(f"/tariffs/{item_id}", json={"price": 280, "status": "архив"})
    assert patched.status_code == 200
    assert patched.json()["price"] == 280


def test_missing():
    assert api().get("/tariffs/99").status_code == 404


def test_delete():
    client = api()
    assert client.delete("/tariffs/1").status_code == 204
    assert client.get("/tariffs/1").status_code == 404


def test_validation():
    response = api().post("/tariffs", json={"name": "", "speed": 0, "price": -1})
    assert response.status_code == 422
