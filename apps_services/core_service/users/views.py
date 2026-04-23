from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from classes.models import Aula 
from pprint import pprint

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
        # CORREÇÃO: Ordenando por data E horário de início para garantir a ordem cronológica correta
        aulas_queryset = Aula.objects.all().order_by('-data', '-horario_inicio')[:5]
        context['aulas_recentes'] = aulas_queryset

        # Debug no console
        print("\n" + "="*80)
        print(f"DEBUG: AULAS RECENTES (Mostrando 5 de {Aula.objects.count()})")
        pprint(list(aulas_queryset.values()), indent=4, width=100)
        print("="*80 + "\n")

    return render(request, 'dashboard.html', context)