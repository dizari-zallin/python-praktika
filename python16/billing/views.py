from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render

from .models import Client, Connection, Payment, Service, Tariff


def index(request):
    return render(request, "billing/index.html", {
        "clients": Client.objects.all(),
        "tariffs": Tariff.objects.all(),
        "services": Service.objects.all(),
    })


def client_detail(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if request.method == "POST":
        action = request.POST.get("action")
        # Новое подключение: тариф обязателен, услуги отмечаются галочками.
        if action == "connect":
            tariff = get_object_or_404(Tariff, pk=request.POST["tariff_id"])
            connection = Connection.objects.create(client=client, tariff=tariff)
            for service_id in request.POST.getlist("services"):
                connection.services.add(service_id)
        # Платёж пишется в историю и сразу увеличивает баланс абонента.
        elif action == "pay":
            amount = Decimal(request.POST["amount"].replace(",", "."))
            Payment.objects.create(client=client, amount=amount, comment=request.POST.get("comment", ""))
            client.balance += amount
            client.save()
        elif action == "status":
            connection = get_object_or_404(Connection, pk=request.POST["connection_id"], client=client)
            connection.status = request.POST["status"]
            connection.save()
        return redirect("client", client_id=client.id)
    return render(request, "billing/client.html", {
        "client": client,
        "tariffs": Tariff.objects.all(),
        "services": Service.objects.all(),
        "connections": client.connections.select_related("tariff").prefetch_related("services"),
        "payments": client.payments.order_by("-created"),
    })
