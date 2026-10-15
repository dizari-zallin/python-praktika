from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("clients/<int:client_id>/", views.client_detail, name="client"),
]
