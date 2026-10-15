"""Прикладной протокол: одно JSON-сообщение на строку."""

import json


class ProtocolError(Exception):
    """Собственное исключение протокола."""


# Одно JSON-сообщение заканчивается переводом строки: так клиент понимает, где граница ответа.
def encode(payload: dict) -> bytes:
    text = json.dumps(payload, ensure_ascii=False)
    return (text + "\n").encode("utf-8")


def decode(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProtocolError("ожидался JSON") from exc
    if not isinstance(data, dict):
        raise ProtocolError("ожидался JSON-объект")
    if "cmd" not in data and "ok" not in data:
        raise ProtocolError("в сообщении нет поля cmd")
    return data


def ok(data):
    return {"ok": True, "data": data}


def fail(message):
    return {"ok": False, "error": message}
