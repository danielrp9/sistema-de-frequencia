from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    Página principal que exibe o dashboard personalizado
    conforme o tipo de usuário (Admin, Professor ou Aluno).
    """
    user = request.user
    context = {
        'user': user,
    }
    
    # Lógica para diferenciar o conteúdo do dashboard
    if user.is_superuser:
        context['tipo'] = 'Administrador'
    elif user.is_professor:
        context['tipo'] = 'Professor'
    elif user.is_aluno:
        context['tipo'] = 'Aluno'
        
    return render(request, 'dashboard.html', context)