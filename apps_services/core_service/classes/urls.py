from django.urls import path
from .views import visualizar_qr_code

urlpatterns = [
    path('aula/<int:aula_id>/qrcode/', visualizar_qr_code, name='visualizar_qr_code'),
]