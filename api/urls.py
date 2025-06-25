from django.urls import path
from .views import (
    LoginView,
    dashboard_profesor,
    dashboard_alumno,
    dashboard_padre,
    registrar_nota,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("dashboard/", dashboard_profesor),
    path("dashboard-alumno/", dashboard_alumno),
    path("dashboard-padre/", dashboard_padre),
    path("registrar-nota/", registrar_nota),
]
