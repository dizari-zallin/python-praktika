"""Начальные данные провайдера."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "provider_site.settings")
django.setup()

from billing.models import Client, Connection, Payment, Service, Tariff


def main():
    if Client.objects.exists():
        print("Данные уже есть")
        return
    home = Tariff.objects.create(name="Домашний 100", speed=100, price=500)
    corp = Tariff.objects.create(name="Корпоративный 500", speed=500, price=2500)
    ip = Service.objects.create(name="белый IP", price=200)
    tv = Service.objects.create(name="ТВ", price=250)
    ivan = Client.objects.create(name="Иванов", phone="79001112233", balance=1200)
    anna = Client.objects.create(name="Петрова", phone="79004445566", balance=300)
    first = Connection.objects.create(client=ivan, tariff=home, status="active")
    first.services.add(tv)
    second = Connection.objects.create(client=anna, tariff=corp, status="active")
    second.services.add(ip)
    Payment.objects.create(client=ivan, amount=1200, comment="аванс")
    print("Тестовые абоненты созданы")


if __name__ == "__main__":
    main()
