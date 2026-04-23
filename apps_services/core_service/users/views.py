from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from classes.models import Aula 

@login_required
def dashboard(request):
    user = request.user
    
    is_professor = getattr(user, 'is_professor', False)
    is_aluno = getattr(user, 'is_aluno', False)
    is_admin = user.is_superuser

    context = {
        'user': user,
        'is_professor': is_professor or is_admin,
        'is_aluno': is_aluno,
        'tipo': 'Administrador' if is_admin else 'Professor' if is_professor else 'Aluno',
    }
    
    if is_professor or is_admin:
        context['aulas_recentes'] = Aula.objects.all().order_by('-data')[:5]
        
    return render(request, 'dashboard.html', context)