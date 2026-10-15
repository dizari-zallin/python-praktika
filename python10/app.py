"""
Лабораторная работа №10. Вариант 20.
REST API тарифов интернет-провайдера (Flask).
"""

from flask import Flask, jsonify, request

from repository import TariffRepository
from service import TariffService

API_KEY = "lab10-key"


def create_app(service=None):
    app = Flask(__name__)
    if service is None:
        service = TariffService(TariffRepository())
        service.create({"name": "Домашний 100", "speed": 100, "price": 500, "region": "Москва"})
        service.create({"name": "Домашний 300", "speed": 300, "price": 800, "region": "Казань"})
        service.create({
            "name": "Корпоративный 500", "speed": 500, "price": 2500,
            "region": "Москва", "services": ["белый IP"],
        })
    app.service = service

    # Ключ в заголовке. Проверка живости сервера /health остаётся открытой.
    @app.before_request
    def check_key():
        if request.path == "/health":
            return None
        if request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "нужен заголовок X-API-Key"}), 401

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/tariffs")
    def list_tariffs():
        status = request.args.get("status")
        sort = request.args.get("sort")
        min_speed = request.args.get("min_speed")
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
        items, total = service.list_tariffs(status, sort, min_speed, page, size)
        return jsonify({"items": items, "total": total, "page": page, "size": size})

    # Специализированная операция варианта: тарифы со скоростью не ниже порога.
    @app.get("/tariffs/by-speed")
    def by_speed():
        min_speed = request.args.get("min_speed", type=int)
        if min_speed is None:
            return jsonify({"error": "укажите min_speed"}), 400
        return jsonify(service.by_speed(min_speed))

    @app.get("/tariffs/<int:item_id>")
    def get_tariff(item_id):
        item = service.repository.get(item_id)
        if item is None:
            return jsonify({"error": "тариф не найден"}), 404
        return jsonify(item)

    # Создание ресурса. Успех — 201 и тело нового тарифа, ошибка данных — 400.
    @app.post("/tariffs")
    def create_tariff():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "ожидался JSON"}), 400
        try:
            item = service.create(data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(item), 201

    @app.put("/tariffs/<int:item_id>")
    def replace_tariff(item_id):
        data = request.get_json(silent=True) or {}
        if service.repository.get(item_id) is None:
            return jsonify({"error": "тариф не найден"}), 404
        try:
            service.validate(data, partial=False)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        payload = {
            "name": data["name"].strip(),
            "speed": int(data["speed"]),
            "price": float(data["price"]),
            "traffic": data.get("traffic", "безлимит"),
            "services": data.get("services") or [],
            "region": data.get("region", "Москва"),
            "status": data.get("status", "активен"),
        }
        return jsonify(service.repository.update(item_id, payload, partial=False))

    # Частичное изменение: в объекте обновляются только присланные поля.
    @app.patch("/tariffs/<int:item_id>")
    def patch_tariff(item_id):
        data = request.get_json(silent=True) or {}
        try:
            service.validate(data, partial=True)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        if "speed" in data:
            data["speed"] = int(data["speed"])
        if "price" in data:
            data["price"] = float(data["price"])
        item = service.repository.update(item_id, data, partial=True)
        if item is None:
            return jsonify({"error": "тариф не найден"}), 404
        return jsonify(item)

    # Удаление без тела ответа: код 204.
    @app.delete("/tariffs/<int:item_id>")
    def delete_tariff(item_id):
        if not service.repository.delete(item_id):
            return jsonify({"error": "тариф не найден"}), 404
        return "", 204

    @app.errorhandler(405)
    def method_not_allowed(_exc):
        return jsonify({"error": "метод не поддерживается"}), 405

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5010, debug=False)
