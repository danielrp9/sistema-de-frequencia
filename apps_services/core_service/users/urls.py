from django.urls import path
from users import views  # Importe explicitamente do app

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    path('gestao/usuarios/', views.gestao_usuarios, name='gestao_usuarios'),
    path('gestao/usuarios/novo/', views.criar_usuario_manual, name='criar_usuario_manual'),
]