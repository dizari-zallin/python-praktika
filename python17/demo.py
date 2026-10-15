"""
Локальный диалог с той же логикой, что и у бота.
Нужен, чтобы показать сценарий без токена Telegram.
"""

import sys

from services import Cabinet

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding="utf-8")


def say(who, text):
    print(f"{who}: {text}")


def main():
    cabinet = Cabinet()
    user_id = 20
    script = [
        ("/start", lambda: cabinet.register(user_id, "Иванов")),
        ("Текущий тариф", lambda: cabinet.current_tariff(user_id)),
        ("/service ТВ", lambda: cabinet.connect_service(user_id, "ТВ")),
        ("История платежей", lambda: cabinet.history(user_id)),
        ("/tariff Домашний 300", lambda: cabinet.change_tariff(user_id, "Домашний 300")),
        ("Текущий тариф", lambda: cabinet.current_tariff(user_id)),
    ]
    say("Бот", "Личный кабинет провайдера. Команды совпадают с aiogram-обработчиками.")
    for command, action in script:
        say("Абонент", command)
        say("Бот", action())
    print("Диалог завершён.")


if __name__ == "__main__":
    main()
