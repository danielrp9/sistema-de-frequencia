from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django_redis import get_redis_connection
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from allauth.account.views import LoginView

from core_config.celery import app as celery_app
from .models import User, Aluno, Professor
from classes.models import Aula 
from academic.models import Turma, Department
from academic.serializers import DisciplinaResumoSerializer
from presence_service.models import Presenca


def get_infra_status():
    using_redis = getattr(settings, 'USE_REDIS_CACHE', False)

    try:
        if using_redis:
            redis_connection = get_redis_connection('default')
            cache_ok = redis_connection.ping()
        else:
            cache.set('dashboard_healthcheck', 'ok', timeout=5)
            cache_ok = cache.get('dashboard_healthcheck') == 'ok'
    except Exception as exc:
        cache_ok = False
        cache_detail = str(exc)
    else:
        cache_detail = getattr(settings, 'REDIS_URL', 'LocMemCache') if using_redis else 'LOCMEMCACHE'

    db_engine = connection.vendor.upper()
    broker_url = getattr(settings, 'CELERY_BROKER_URL', '')
    try:
        worker_responses = celery_app.control.ping(timeout=0.5) if broker_url else []
    except Exception as exc:
        queue_status = 'INDISPONIVEL'
        queue_detail = str(exc)
    else:
        if worker_responses:
            worker_names = [
                list(response.keys())[0]
                for response in worker_responses
                if response
            ]
            queue_status = 'ONLINE'
            queue_detail = f"WORKERS: {', '.join(worker_names)}"
        elif broker_url:
            queue_status = 'SEM WORKER'
            queue_detail = broker_url
        else:
            queue_status = 'NAO CONFIGURADO'
            queue_detail = 'BROKER AUSENTE'

    return {
        'cache': {
            'name': 'Redis Cache' if using_redis else 'Cache Local',
            'status': 'ONLINE' if cache_ok else 'INDISPONIVEL',
            'detail': cache_detail,
        },
        'queue': {
            'name': 'Celery / RabbitMQ',
            'status': queue_status,
            'detail': queue_detail,
        },
        'database': {
            'name': 'Banco de Dados',
            'status': db_engine,
            'detail': 'POSTGRESQL' if connection.vendor == 'postgresql' else 'DESENVOLVIMENTO',
        },
    }


def build_turmas_chart_data(turmas):
    labels = []
    presencas = []
    faltas = []

    for turma in turmas[:8]:
        aulas_count = Aula.objects.filter(turma=turma).count()
        alunos_count = turma.alunos.count()
        total_previsto = aulas_count * alunos_count
        total_presencas = Presenca.objects.filter(aula__turma=turma, status='VALIDA').count()

        labels.append(f"{turma.disciplina.codigo} {turma.semestre}")
        presencas.append(total_presencas)
        faltas.append(max(total_previsto - total_presencas, 0))

    return {
        'labels': labels,
        'presencas': presencas,
        'faltas': faltas,
        'resumo': {
            'labels': ['Presencas', 'Faltas'],
            'values': [sum(presencas), sum(faltas)],
        },
    }


def build_aluno_chart_data(disciplinas):
    return {
        'labels': [disciplina['codigo'] for disciplina in disciplinas],
        'frequencia': [disciplina['porcentagem_frequencia'] for disciplina in disciplinas],
        'presencas': [disciplina['horas_presenca'] for disciplina in disciplinas],
        'faltas': [disciplina['horas_falta'] for disciplina in disciplinas],
    }


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
        # Lista todas as turmas ativas para supervisão básica
        context['turmas_sistema'] = Turma.objects.filter(ativa=True).select_related('disciplina', 'professor')[:10]
        context['infra_status'] = get_infra_status()
    
    elif is_professor:
        minhas_turmas = Turma.objects.filter(professor__user=user, ativa=True).select_related('disciplina')
        context['minhas_turmas'] = minhas_turmas
        context['aulas_recentes'] = Aula.objects.filter(turma__professor__user=user).order_by('-data', '-horario_inicio')[:5]
        context['chart_data'] = build_turmas_chart_data(list(minhas_turmas))

    if is_aluno:
        try:
            turmas = Turma.objects.filter(alunos__user=user, ativa=True).select_related('disciplina', 'professor')
            disciplinas = [t.disciplina for t in turmas]
            # No dashboard inicial, apenas listamos as turmas para não sobrecarregar
            serializer = DisciplinaResumoSerializer(disciplinas, many=True, context={'aluno': user.perfil_aluno})
            
            # Mapeamos os dados serializados de volta para as turmas para ter acesso ao ID da Turma no template
            turmas_data = []
            for i, t in enumerate(turmas):
                item = serializer.data[i]
                item['turma_id'] = t.id
                item['professor_nome'] = t.professor.nome
                turmas_data.append(item)
                
            context['disciplinas_aluno'] = turmas_data
        except Exception:
            context['disciplinas_aluno'] = []

    return render(request, 'dashboard.html', context)

@login_required
def detalhes_disciplina_aluno(request, turma_id):
    """Visão detalhada de uma disciplina para o aluno."""
    if not getattr(request.user, 'is_aluno', False):
        return redirect('dashboard')
        
    turma = get_object_or_404(Turma, id=turma_id, alunos__user=request.user)
    aluno = request.user.perfil_aluno
    
    # Histórico de Presenças
    aulas = Aula.objects.filter(turma=turma).order_by('data', 'horario_inicio')
    presencas_aluno = Presenca.objects.filter(aluno=aluno, aula__turma=turma, status='VALIDA').values_list('aula_id', flat=True)
    
    historico = []
    for aula in aulas:
        historico.append({
            'data': aula.data,
            'presente': aula.id in presencas_aluno,
            'peso': aula.peso_aula
        })
        
    # Estatísticas
    serializer = DisciplinaResumoSerializer(turma.disciplina, context={'aluno': aluno})
    
    context = {
        'turma': turma,
        'disciplina': turma.disciplina,
        'historico': historico,
        'stats': serializer.data,
        'chart_data': {
            'labels': ['Presenças', 'Faltas'],
            'values': [serializer.data['horas_presenca'], serializer.data['horas_falta']]
        }
    }
    return render(request, 'users/detalhes_disciplina_aluno.html', context)

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


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AccountLoginView(LoginView):
    template_name = 'account/login.html'
