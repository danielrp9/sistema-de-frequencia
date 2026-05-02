from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Aluno, Professor
from classes.models import Aula 
from academic.models import Turma, Department
from academic.serializers import DisciplinaResumoSerializer

# --- ACESSO AO DASHBOARD ---
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
        'tipo': 'Administrador' if is_admin else 'Professor' if is_professor else 'Estudante',
    }

    if is_admin:
        context['departamentos'] = Department.objects.all()
        context['minhas_turmas'] = Turma.objects.filter(ativa=True).select_related('disciplina')
        context['aulas_recentes'] = Aula.objects.all().order_by('-data', '-horario_inicio')[:10]
    
    elif is_professor:
        context['minhas_turmas'] = Turma.objects.filter(professor__user=user, ativa=True).select_related('disciplina')
        context['aulas_recentes'] = Aula.objects.filter(turma__professor__user=user).order_by('-data', '-horario_inicio')[:5]

    if is_aluno:
        try:
            turmas = Turma.objects.filter(alunos__user=user, ativa=True)
            disciplinas = [t.disciplina for t in turmas]
            # Cálculo de limite de faltas para o serializer/contexto
            serializer = DisciplinaResumoSerializer(disciplinas, many=True, context={'aluno': user.perfil_aluno})
            context['disciplinas_aluno'] = serializer.data
        except Exception:
            context['disciplinas_aluno'] = []

    return render(request, 'dashboard.html', context)

# --- GESTÃO DE USUÁRIOS (ADMIN ONLY) ---
def admin_only(user):
    return user.is_superuser

@user_passes_test(admin_only)
def gestao_usuarios(request):
    usuarios = User.objects.all().order_by('-date_joined')
    role = request.GET.get('role')
    if role == 'professor':
        usuarios = usuarios.filter(is_professor=True)
    elif role == 'aluno':
        usuarios = usuarios.filter(is_aluno=True)

    context = {
        'usuarios': usuarios,
        'total_professores': User.objects.filter(is_professor=True).count(),
        'total_alunos': User.objects.filter(is_aluno=True).count(),
    }
    return render(request, 'users/gestao_usuarios.html', context)

@user_passes_test(admin_only)
def criar_usuario_manual(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "ERRO_DUP: Nome de usuário já existe.")
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_professor=(role == 'professor'),
                is_aluno=(role == 'aluno')
            )
            messages.success(request, f"NODE_CREATED: Usuário {username} registrado como {role}.")
            return redirect('gestao_usuarios')
    return render(request, 'users/form_usuario.html')