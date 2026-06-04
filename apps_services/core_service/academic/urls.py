from django.urls import path
from . import views

urlpatterns = [
    # Rotas Institucionais (Admin)
    path('departamentos/', views.gestao_departamentos, name='gestao_departamentos'),
    path('departamentos/<int:depto_id>/', views.detalhes_departamento, name='detalhes_departamento'),
    
    # Rota de Gestão de Alunos (Professor/Admin)
    path('gestao-turma/', views.lista_turmas_gestao, name='lista_turmas_gestao'),
    path('gestao-turma/<int:turma_id>/', views.gerenciar_alunos_disciplina, name='gerenciar_alunos_disciplina'),
    path('gestao-turma/<int:turma_id>/frequencia/', views.folha_frequencia_turma, name='folha_frequencia_turma'),
    path('gestao-turma/<int:turma_id>/reprovados/', views.alunos_reprovados_turma, name='alunos_reprovados_turma'),
    path('gestao-turma/<int:turma_id>/encerrar/', views.encerrar_turma, name='encerrar_turma'),
    path('cursos/<int:curso_id>/', views.detalhes_curso, name='detalhes_curso'),
    path('disciplinas/<int:disciplina_id>/', views.detalhes_disciplina, name='detalhes_disciplina'),
    path('abrir-turma/', views.abrir_turma, name='abrir_turma'),
    path('salas/gestao/', views.gestao_salas, name='gestao_salas'),
]