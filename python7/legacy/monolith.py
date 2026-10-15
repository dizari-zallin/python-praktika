"""
Первоначальная версия (для анализа нарушений SOLID).
Один класс одновременно хранит данные, считает оплату, печатает отчёт
и сам создаёт файловое хранилище. Новый тариф требует правки if/elif.
"""


class ProviderMonolith:
    def __init__(self):
        self.clients = []
        self.path = "clients.txt"

    def connect_client(self, name, tariff_code, months):
        # Нарушение OCP: новая стратегия — новая ветка в этом методе.
        if tariff_code == "home":
            payment = 500 * months
        elif tariff_code == "corp":
            payment = 2500 * months * 0.9
        elif tariff_code == "mobile":
            payment = 350 * months
        else:
            raise ValueError("неизвестный тариф")
        self.clients.append({"name": name, "tariff": tariff_code, "payment": payment, "blocked": False})
        self.save_and_print_report()
        return payment

    def change_tariff(self, name, tariff_code, months):
        for client in self.clients:
            if client["name"] == name:
                client["tariff"] = tariff_code
                return self.connect_client(name + "_copy", tariff_code, months)
        return None

    def block(self, name):
        for client in self.clients:
            if client["name"] == name:
                client["blocked"] = True

    def save_and_print_report(self):
        # Нарушение SRP: сохранение и отчёт смешаны с подключением.
        lines = []
        for client in self.clients:
            line = f"{client['name']};{client['tariff']};{client['payment']}"
            lines.append(line)
            print("ОТЧЁТ:", line)
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

    def charge_external_api(self, client):
        # Нарушение DIP: конкретный способ оплаты зашит в класс.
        print("Списание через конкретный банк:", client["name"])
