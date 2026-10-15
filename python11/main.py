"""
Лабораторная работа №11. Вариант 20.
SQLite, документные расчёты, кэш и статика тарифов.
"""

import sys

from cache_and_docs import CalculationStore, PriceCache, cdn_headers, write_static
from database import add_tariff_with_service, connect, explain_index, init_db, showcase_queries

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


def print_menu():
    print()
    print("===== Хранение тарифов =====")
    print("1. Показать SQL-запросы")
    print("2. План запроса по индексу скорости")
    print("3. Добавить тариф с услугой (транзакция)")
    print("4. Расчёт стоимости через кэш")
    print("5. Сохранить расчёт в документную БД")
    print("6. Статика и CDN")
    print("0. Выход")
    print()


def price_from_sql(conn, name):
    row = conn.execute("SELECT price FROM tariffs WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise ValueError("тариф не найден")
    services = conn.execute(
        """
        SELECT COALESCE(SUM(s.price), 0)
        FROM tariff_services ts
        JOIN services s ON s.id = ts.service_id
        JOIN tariffs t ON t.id = ts.tariff_id
        WHERE t.name = ?
        """,
        (name,),
    ).fetchone()[0]
    return row["price"] + services


def main():
    conn = connect()
    init_db(conn)
    cache = PriceCache()
    docs = CalculationStore()
    print("База открыта, внешние ключи включены, тестовые тарифы загружены.")

    while True:
        print_menu()
        choice = read_line("Выберите действие: ")
        try:
            if choice == "1":
                print("\nЗапросы выполняются с параметрами ?, не через склейку строк.")
                for title, count, preview in showcase_queries(conn):
                    print(f"\n{title}: строк {count}")
                    for row in preview:
                        print(" ", row)
            elif choice == "2":
                print("EXPLAIN QUERY PLAN для speed >= 100:")
                for row in explain_index(conn):
                    print(" ", row)
                print("Индекс idx_tariffs_speed позволяет не просматривать всю таблицу при отборе по скорости.")
            elif choice == "3":
                name = read_line("Название: ")
                speed = int(read_line("Скорость: "))
                price = float(read_line("Цена: ").replace(",", "."))
                region = read_line("Регион (Москва/Казань/Тула): ")
                service = read_line("Услуга (белый IP/антивирус/ТВ/статический IP): ")
                item_id = add_tariff_with_service(conn, name, speed, price, region, service)
                print(f"Транзакция зафиксирована, id = {item_id}")
            elif choice == "4":
                name = read_line("Название тарифа: ")
                key = f"price:{name}"
                total, source = cache.get_total(key, lambda: price_from_sql(conn, name))
                print(f"Сумма {total:.0f} руб., источник: {source}")
                total2, source2 = cache.get_total(key, lambda: price_from_sql(conn, name))
                print(f"Повторный запрос {total2:.0f} руб., источник: {source2}")
                print(f"Попадания в кэш: {cache.hits}, промахи: {cache.misses}, TTL 60 с")
            elif choice == "5":
                name = read_line("Название тарифа: ")
                total = price_from_sql(conn, name)
                docs.save(name, total, ["базовая плата", "услуги"])
                saved = docs.latest(name)
                print("Документ расчёта:", {k: saved[k] for k in ("tariff", "total", "services")})
            elif choice == "6":
                path = write_static()
                print("Файл изображения:", path)
                print("Заголовки CDN:", cdn_headers())
                print("Картинку тарифа отдают с CDN: она публичная и меняется редко.")
                print("Версия в имени файла (home100.v1.svg) позволяет не сбрасывать кэш всего сайта.")
            elif choice == "0":
                print("Работа программы завершена.")
                break
            else:
                print("Ошибка: выберите пункт от 0 до 6.")
        except (ValueError, Exception) as exc:
            if isinstance(exc, (EOFError, KeyboardInterrupt)):
                raise
            print(f"Ошибка: {exc}")
        except EOFError:
            break
    conn.close()


if __name__ == "__main__":
    main()
