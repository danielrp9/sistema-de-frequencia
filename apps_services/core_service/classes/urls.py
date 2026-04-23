from django.urls import path
from .views import visualizar_qr_code, encerrar_aula # Adicione a importação aqui

urlpatterns = [
    path('aula/<int:aula_id>/qrcode/', visualizar_qr_code, name='visualizar_qr_code'),
    path('aula/<int:aula_id>/encerrar/', encerrar_aula, name='encerrar_aula'),
]