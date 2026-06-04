from django.urls import path
from users import views  # Importe explicitamente do app

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cadastro/aluno/', views.AlunoSignupView.as_view(), name='signup_aluno'),
    path('cadastro/professor/', views.ProfessorSignupView.as_view(), name='signup_professor'),
    path('cadastro/escolha/', views.signup_choice, name='signup_choice'),
    
    path('gestao/usuarios/', views.gestao_usuarios, name='gestao_usuarios'),
    path('gestao/usuarios/<int:user_id>/', views.detalhes_usuario, name='detalhes_usuario'),
    path('gestao/usuarios/<int:user_id>/aprovar/', views.aprovar_usuario, name='aprovar_usuario'),
    path('gestao/usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('gestao/usuarios/novo/', views.criar_usuario_manual, name='criar_usuario_manual'),
    path('gestao/historico/', views.historico_sistema, name='historico_sistema'),
    path('historico-turmas/', views.historico_turmas_professor, name='historico_turmas_professor'),
    path('perfil/', views.meu_perfil, name='meu_perfil'),
    path('notificacao/<int:notif_id>/ler/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('notificacoes/limpar/', views.limpar_notificacoes, name='limpar_notificacoes'),
    path('disciplina/<int:turma_id>/', views.detalhes_disciplina_aluno, name='detalhes_disciplina_aluno'),
]