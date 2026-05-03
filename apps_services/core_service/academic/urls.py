from django.urls import path
from . import views

urlpatterns = [
    # Rotas Institucionais (Admin)
    path('departamentos/', views.gestao_departamentos, name='gestao_departamentos'),
    path('departamentos/<int:depto_id>/', views.detalhes_departamento, name='detalhes_departamento'),
    
    # Rota de Gestão de Alunos (Professor/Admin)
    path('gestao-turma/<int:turma_id>/', views.gerenciar_alunos_disciplina, name='gerenciar_alunos_disciplina'),
    path('cursos/<int:curso_id>/', views.detalhes_curso, name='detalhes_curso'),
    path('abrir-turma/', views.abrir_turma, name='abrir_turma'),
    path('salas/gestao/', views.gestao_salas, name='gestao_salas'),
]