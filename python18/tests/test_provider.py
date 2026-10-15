"""Проверки варианта 20: регистрация, тариф, смена, стоимость, блокировка."""

import os
import sys
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from provider import Provider, ProviderError


def test_register():
    provider = Provider()
    person = provider.register("Иванов", "7900")
    assert person["name"] == "Иванов"
    assert person["tariff"] is None


def test_register_duplicate():
    provider = Provider()
    provider.register("Иванов", "7900")
    with pytest.raises(ProviderError):
        provider.register("Другой", "7900")


def test_connect_tariff():
    provider = Provider()
    provider.register("Петрова", "7911")
    assert provider.connect("7911", "Домашний 100") == 500


def test_change_tariff():
    provider = Provider()
    provider.register("Петрова", "7911")
    provider.connect("7911", "Домашний 100")
    assert provider.change_tariff("7911", "Корпоративный 500") == 2500


def test_cost_without_tariff():
    provider = Provider()
    provider.register("Сидоров", "7922")
    assert provider.cost("7922") == 0


def test_block_on_debt():
    provider = Provider()
    provider.register("Орлов", "7933")
    provider.connect("7933", "Домашний 300")
    person = provider.charge("7933")
    assert person["balance"] == -800
    assert person["blocked"] is True


def test_blocked_cannot_change_tariff():
    provider = Provider()
    provider.register("Орлов", "7933")
    provider.connect("7933", "Домашний 100")
    provider.charge("7933")
    with pytest.raises(ProviderError):
        provider.change_tariff("7933", "Домашний 300")


def test_payment_unblocks():
    provider = Provider()
    provider.register("Орлов", "7933")
    provider.connect("7933", "Домашний 100")
    provider.charge("7933")
    person = provider.pay("7933", 500)
    assert person["blocked"] is False


def test_gateway_called_with_mock():
    gateway = Mock()
    gateway.charge.return_value = {"status": "ok"}
    provider = Provider()
    provider.register("Иванов", "7900")
    provider.connect("7900", "Домашний 100")
    result = gateway.charge(phone="7900", amount=provider.cost("7900"))
    gateway.charge.assert_called_once_with(phone="7900", amount=500)
    assert result["status"] == "ok"
