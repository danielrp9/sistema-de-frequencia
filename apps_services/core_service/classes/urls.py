from django.urls import path
from . import views
from academic.views import gerenciar_alunos_disciplina

urlpatterns = [
    # Rota para o formulário de lançamento de aula do professor
    path('lancar/', views.registrar_aula, name='registrar_aula'),
    
    # Rotas de gerenciamento de aula e QR Code
    path('qr/<int:aula_id>/', views.visualizar_qr_code, name='visualizar_qr_code'),
    path('encerrar/<int:aula_id>/', views.encerrar_aula, name='encerrar_aula'),
    path('scanner/', views.registrar_presenca_camera, name='registrar_presenca_camera'),
    path('relatorio/<int:turma_id>/', views.relatorio_presenca_disciplina, name='relatorio_presenca_disciplina'),
]