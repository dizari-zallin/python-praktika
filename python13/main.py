"""
Лабораторная работа №13. Вариант 20.
Тарифы в документной БД и кэш Redis.
Локальный запуск использует совместимые in-memory серверы с тем же API.
"""

import sys

import fakeredis
import mongomock

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")


def read_line(prompt):
    if sys.stdin.isatty():
        return input(prompt).strip()
    raw = sys.stdin.readline()
    if raw == "":
        raise EOFError
    text = raw.rstrip("\r\n")
    print(f"{prompt}{text}")
    return text.strip()


class TariffApp:
    def __init__(self):
        self.mongo = mongomock.MongoClient()
        self.tariffs = self.mongo["provider"]["tariff"]
        self.redis = fakeredis.FakeRedis(decode_responses=True)
        self._seed()

    def _seed(self):
        if self.tariffs.count_documents({}) == 0:
            self.tariffs.insert_many([
                {"name": "Домашний 100", "speed": 100, "price": 500, "limits": "безлимит",
                 "services": ["антивирус"], "region": "Москва", "status": "активен"},
                {"name": "Домашний 300", "speed": 300, "price": 800, "limits": "безлимит",
                 "services": ["ТВ"], "region": "Казань", "status": "активен"},
                {"name": "Корпоративный 500", "speed": 500, "price": 2500, "limits": "гарантия 99%",
                 "services": ["белый IP", "статический IP"], "region": "Москва", "status": "активен"},
                {"name": "Архив 50", "speed": 50, "price": 200, "limits": "100 ГБ",
                 "services": [], "region": "Тула", "status": "архив"},
            ])

    def list_tariffs(self):
        return list(self.tariffs.find({}, {"_id": 0}))

    # Просмотр увеличивает счётчик в отсортированном множестве популярных тарифов.
    def remember_popular(self, name):
        self.redis.zincrby("popular_tariffs", 1, name)

    def popular(self, limit=3):
        return self.redis.zrevrange("popular_tariffs", 0, limit - 1, withscores=True)

    # Повторное сравнение берётся из Redis, пока ключ не истёк.
    def compare(self, left, right):
        key = f"compare:{left}:{right}"
        cached = self.redis.get(key)
        if cached:
            return cached, "cache"
        a = self.tariffs.find_one({"name": left})
        b = self.tariffs.find_one({"name": right})
        if not a or not b:
            raise ValueError("один из тарифов не найден")
        text = (
            f"{a['name']}: {a['speed']} Мбит/с за {a['price']} руб.; "
            f"{b['name']}: {b['speed']} Мбит/с за {b['price']} руб."
        )
        self.redis.setex(key, 120, text)
        return text, "mongo"

    # Стоимость = цена тарифа плюс 100 рублей за каждую услугу. Повтор читает кэш.
    def quote(self, name):
        key = f"quote:{name}"
        cached = self.redis.get(key)
        if cached:
            return float(cached), "cache"
        tariff = self.tariffs.find_one({"name": name})
        if tariff is None:
            raise ValueError("тариф не найден")
        extra = 100 * len(tariff.get("services") or [])
        total = tariff["price"] + extra
        self.redis.setex(key, 60, str(total))
        return total, "mongo"


def print_tariff(item):
    services = ", ".join(item["services"]) if item["services"] else "нет"
    print(
        f"{item['name']}: {item['speed']} Мбит/с, {item['price']} руб., "
        f"{item['region']}, {item['status']}, услуги: {services}, лимит: {item['limits']}"
    )


def print_menu():
    print()
    print("===== MongoDB + Redis: тарифы =====")
    print("1. Документы тарифов")
    print("2. Отметить просмотр популярного тарифа")
    print("3. Популярные тарифы")
    print("4. Сравнить два тарифа")
    print("5. Кэш расчёта стоимости")
    print("0. Выход")
    print()


def main():
    app = TariffApp()
    print("Коллекция tariff и ключи Redis готовы.")
    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            if choice == "1":
                for item in app.list_tariffs():
                    print_tariff(item)
            elif choice == "2":
                name = read_line("Название тарифа: ")
                app.remember_popular(name)
                print("Счётчик просмотров увеличен.")
            elif choice == "3":
                rows = app.popular()
                if not rows:
                    print("Популярных тарифов ещё нет.")
                for name, score in rows:
                    print(f"  {name}: {int(score)}")
            elif choice == "4":
                left = read_line("Первый тариф: ")
                right = read_line("Второй тариф: ")
                text, source = app.compare(left, right)
                print(f"[{source}] {text}")
                text2, source2 = app.compare(left, right)
                print(f"Повтор [{source2}] {text2}")
            elif choice == "5":
                name = read_line("Название тарифа: ")
                total, source = app.quote(name)
                print(f"[{source}] к оплате {total:.0f} руб.")
                total2, source2 = app.quote(name)
                print(f"Повтор [{source2}] {total2:.0f} руб.")
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: выберите пункт от 0 до 5.")
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except EOFError:
            break


if __name__ == "__main__":
    main()
