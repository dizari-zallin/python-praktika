"""Наивный расчёт без паттернов: ветки if и прямое создание объектов."""


def create_tariff(kind, name):
    if kind == "home":
        return {"kind": kind, "name": name, "fee": 500, "discount": 0}
    if kind == "corp":
        return {"kind": kind, "name": name, "fee": 2500, "discount": 0.1}
    if kind == "mobile":
        return {"kind": kind, "name": name, "fee": 350, "discount": 0}
    raise ValueError("неизвестный вид")


def month_price(tariff, extras):
    fee = tariff["fee"]
    discount = tariff["fee"] * tariff["discount"]
    extra = 100 * extras
    return fee - discount + extra
