from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({"message": "Bienvenido a la API de la escuela"})

urlpatterns = [
    path('', root_view),  # 👈 esta es la raíz del sitio
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
