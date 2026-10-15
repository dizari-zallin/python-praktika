from django.contrib import admin

from .models import Client, Connection, Payment, Service, Tariff

admin.site.register(Client)
admin.site.register(Tariff)
admin.site.register(Service)
admin.site.register(Connection)
admin.site.register(Payment)
