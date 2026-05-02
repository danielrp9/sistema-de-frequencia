from django.urls import path
from .views import registrar_presenca

urlpatterns = [
    path('registrar/', registrar_presenca, name='registrar_presenca'),
]