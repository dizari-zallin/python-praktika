from django.db import models


class Client(models.Model):
    name = models.CharField("имя", max_length=120)
    phone = models.CharField("телефон", max_length=20)
    balance = models.DecimalField("баланс", max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField("название", max_length=120)
    speed = models.PositiveIntegerField("скорость, Мбит/с")
    price = models.DecimalField("цена", max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField("услуга", max_length=120)
    price = models.DecimalField("цена", max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Connection(models.Model):
    STATUS = [("active", "активно"), ("suspended", "приостановлено"), ("disabled", "отключено")]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="connections")
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT, related_name="connections")
    services = models.ManyToManyField(Service, blank=True, related_name="connections")
    status = models.CharField("статус", max_length=20, choices=STATUS, default="active")
    started = models.DateField("дата подключения", auto_now_add=True)

    # К оплате: цена тарифа плюс услуги. Неактивное подключение сейчас ничего не начисляет.
    def monthly_total(self):
        extra = sum(service.price for service in self.services.all())
        if self.status != "active":
            return 0
        return self.tariff.price + extra


class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField("сумма", max_digits=10, decimal_places=2)
    comment = models.CharField("комментарий", max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
