from django.urls import path
from .views import registrar_presenca, registrar_presenca_api

urlpatterns = [
    path('registrar/', registrar_presenca, name='registrar_presenca'),
    path('api/registrar/', registrar_presenca_api, name='api_registrar_presenca'),
]