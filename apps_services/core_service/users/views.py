from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Sum
from django_redis import get_redis_connection
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from allauth.account.views import LoginView, SignupView
from .forms import AlunoSignupForm, ProfessorSignupForm

class AlunoSignupView(SignupView):
    template_name = 'account/signup_aluno.html'
    form_class = AlunoSignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.user
        user.is_aluno = True
        user.is_approved = True
        user.save()
        
        # Atualiza ou cria o perfil com os dados do form
        aluno_perfil, _ = Aluno.objects.get_or_create(user=user)
        aluno_perfil.nome = form.cleaned_data.get('nome_completo')
        aluno_perfil.matricula = form.cleaned_data.get('matricula')
        aluno_perfil.email = user.email
        aluno_perfil.save()
        return response

class ProfessorSignupView(SignupView):
    template_name = 'account/signup_professor.html'
    form_class = ProfessorSignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.user
        user.is_professor = True
        user.is_approved = False
        user.save()

        # Atualiza ou cria o perfil com os dados do form
        prof_perfil, _ = Professor.objects.get_or_create(user=user)
        prof_perfil.nome = form.cleaned_data.get('nome_completo')
        prof_perfil.siape = form.cleaned_data.get('siape')
        prof_perfil.email = user.email
        prof_perfil.save()
        return response

def signup_choice(request):
    return render(request, 'account/signup.html')

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


from django.urls import reverse
from .models import User, Aluno, Professor, Notification
from .services import NotificationService

@login_required
def marcar_notificacao_lida(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('dashboard')

@login_required
def limpar_notificacoes(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Todas as notificações foram limpas.")
    return redirect('dashboard')

# --- ACESSO AO DASHBOARD ---
@login_required
def dashboard(request):
    user = request.user
    
    # Validação de Aprovação para Professores
    if getattr(user, 'is_professor', False) and not getattr(user, 'is_approved', True):
        return render(request, 'users/aguardando_aprovacao.html')

    is_professor = getattr(user, 'is_professor', False)
    is_aluno = getattr(user, 'is_aluno', False)
    is_admin = user.is_superuser

    # Sincronização Dinâmica de Notificações (Service Layer)
    NotificationService.sync_professor_notifications(user)
    NotificationService.sync_student_notifications(user)

    if is_admin:
        pendentes = User.objects.filter(is_professor=True, is_approved=False).count()
        if pendentes > 0:
            link = reverse('gestao_usuarios') + "?role=professor"
            if not Notification.objects.filter(user=user, link=link, is_read=False).exists():
                Notification.objects.create(user=user, title="Aprovação Pendente", message=f"{pendentes} professores aguardam aprovação.", link=link, type='warning')

    notificacoes_qs = Notification.objects.filter(user=user, is_read=False)

    context = {
        'user': user,
        'is_professor': is_professor,
        'is_aluno': is_aluno,
        'is_admin': is_admin,
        'tipo': 'Administrador' if is_admin else 'Professor' if is_professor else 'Estudante',
        'notificacoes': notificacoes_qs,
    }

    # Consolidação de Aulas para o Dashboard (Prioridade para o que o usuário precisa ver)
    aulas_recentes = []
    if is_admin:
        context['departamentos'] = Department.objects.all()
        context['infra_status'] = get_infra_status()
        # Admin vê as 10 últimas do sistema para supervisão global
        aulas_recentes = Aula.objects.all().order_by('-data', '-horario_inicio')[:10]
    elif is_professor:
        # Professor vê as suas 10 últimas aulas
        aulas_recentes = Aula.objects.filter(
            turma__professor__user=user
        ).order_by('-data', '-horario_inicio')[:10]
    
    context['aulas_recentes'] = aulas_recentes

    if is_professor:
        minhas_turmas = Turma.objects.filter(professor__user=user, ativa=True).select_related('disciplina')
        context['minhas_turmas'] = minhas_turmas
        
        context['chart_data'] = build_turmas_chart_data(list(minhas_turmas))

    if is_aluno:
        try:
            turmas = Turma.objects.filter(alunos__user=user, ativa=True).select_related('disciplina', 'professor')
            disciplinas = [t.disciplina for t in turmas]
            serializer = DisciplinaResumoSerializer(disciplinas, many=True, context={'aluno': user.perfil_aluno})
            
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
def historico_turmas_professor(request):
    """Exibe o histórico de turmas encerradas do professor."""
    if not getattr(request.user, 'is_professor', False):
        return redirect('dashboard')
    
    professor_perfil = get_object_or_404(Professor, user=request.user)
    turmas_encerradas = Turma.objects.filter(professor=professor_perfil, ativa=False).select_related('disciplina').order_by('-id')
    
    return render(request, 'academic/historico_turmas_professor.html', {
        'turmas_encerradas': turmas_encerradas
    })

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
def aprovar_usuario(request, user_id):
    user_to_approve = get_object_or_404(User, id=user_id)
    user_to_approve.is_approved = True
    user_to_approve.save()
    
    # Notificação para o professor aprovado
    Notification.objects.create(
        user=user_to_approve,
        title="Acesso Liberado",
        message=f"Olá {user_to_approve.first_name}, seu acesso como Docente foi aprovado. Agora você tem acesso total ao sistema.",
        type='info'
    )
    
    messages.success(request, f"ACCESS_GRANTED: O acesso de {user_to_approve.username} foi liberado.")
    return redirect('gestao_usuarios')

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
        'current_role': role or 'all',
    }
    return render(request, 'users/gestao_usuarios.html', context)

@user_passes_test(admin_only)
def criar_usuario_manual(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        nome_completo = request.POST.get('nome_completo')
        password = request.POST.get('password')
        role = request.POST.get('role')
        identificador = request.POST.get('identificador')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "ERRO_DUP: Este e-mail já está cadastrado.")
        else:
            new_user = User.objects.create_user(
                username=email,  # Username é o e-mail
                email=email,
                password=password,
                first_name=nome_completo,
                is_professor=(role == 'professor'),
                is_aluno=(role == 'aluno'),
                is_approved=True
            )
            
            if role == 'aluno':
                aluno_perfil, _ = Aluno.objects.get_or_create(user=new_user)
                aluno_perfil.matricula = identificador
                aluno_perfil.save()
            elif role == 'professor':
                prof_perfil, _ = Professor.objects.get_or_create(user=new_user)
                prof_perfil.siape = identificador
                prof_perfil.save()

            messages.success(request, f"NODE_CREATED: Usuário {email} registrado como {role}.")
            return redirect('gestao_usuarios')
    return render(request, 'users/form_usuario.html')

@user_passes_test(admin_only)
def detalhes_usuario(request, user_id):
    """Exibe os dados do usuário em modo leitura antes da edição."""
    user_obj = get_object_or_404(User, id=user_id)
    identificador = "N/A"
    perfil = None
    if user_obj.is_aluno and hasattr(user_obj, 'perfil_aluno'):
        perfil = user_obj.perfil_aluno
        identificador = perfil.matricula
    elif user_obj.is_professor and hasattr(user_obj, 'perfil_professor'):
        perfil = user_obj.perfil_professor
        identificador = perfil.siape

    return render(request, 'users/detalhes_usuario.html', {
        'user_obj': user_obj,
        'perfil': perfil,
        'identificador': identificador,
        'tipo_identificador': 'SIAPE' if user_obj.is_professor else 'Matrícula'
    })

@user_passes_test(admin_only)
def editar_usuario(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    perfil = None
    if user_to_edit.is_aluno and hasattr(user_to_edit, 'perfil_aluno'):
        perfil = user_to_edit.perfil_aluno
    elif user_to_edit.is_professor and hasattr(user_to_edit, 'perfil_professor'):
        perfil = user_to_edit.perfil_professor

    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo')
        email = request.POST.get('email')
        role = request.POST.get('role')
        identificador = request.POST.get('identificador')
        is_approved = request.POST.get('is_approved') == 'on'
        
        # Novos campos
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        nome_pai = request.POST.get('nome_pai')
        nome_mae = request.POST.get('nome_mae')

        user_to_edit.first_name = nome_completo
        user_to_edit.email = email
        user_to_edit.username = email
        user_to_edit.is_professor = (role == 'professor')
        user_to_edit.is_aluno = (role == 'aluno')
        user_to_edit.is_approved = is_approved
        user_to_edit.save()

        if role == 'aluno':
            p, _ = Aluno.objects.get_or_create(user=user_to_edit)
            p.nome = nome_completo
            p.email = email
            p.matricula = identificador
            p.telefone = telefone
            p.endereco = endereco
            p.nome_pai = nome_pai
            p.nome_mae = nome_mae
            p.save()
        elif role == 'professor':
            p, _ = Professor.objects.get_or_create(user=user_to_edit)
            p.nome = nome_completo
            p.email = email
            p.siape = identificador
            p.telefone = telefone
            p.endereco = endereco
            p.save()

        messages.success(request, f"NODE_UPDATED: Dados de {user_to_edit.get_full_name()} atualizados.")
        return redirect('gestao_usuarios')

    identificador = ""
    if user_to_edit.is_aluno and perfil:
        identificador = perfil.matricula
    elif user_to_edit.is_professor and perfil:
        identificador = perfil.siape

    return render(request, 'users/form_usuario.html', {
        'edit_mode': True,
        'user_to_edit': user_to_edit,
        'perfil': perfil,
        'identificador': identificador
    })

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def meu_perfil(request):
    """Módulo de perfil pessoal para visualização e edição de dados biográficos."""
    user = request.user
    perfil = None
    tipo_id = "N/A"
    identificador = "N/A"

    if user.is_aluno:
        perfil = getattr(user, 'perfil_aluno', None)
        tipo_id = "Matrícula"
        identificador = perfil.matricula if perfil else "N/A"
    elif user.is_professor:
        perfil = getattr(user, 'perfil_professor', None)
        tipo_id = "SIAPE"
        identificador = perfil.siape if perfil else "N/A"

    edit_mode = request.GET.get('edit') == 'true'
    password_mode = request.GET.get('password') == 'true'
    
    password_form = PasswordChangeForm(user)

    if request.method == "POST":
        if 'btn_save_profile' in request.POST and perfil:
            # Todos os dados pessoais podem ser editados, exceto e-mail
            novo_nome = request.POST.get('nome')
            perfil.nome = novo_nome
            perfil.telefone = request.POST.get('telefone')
            perfil.endereco = request.POST.get('endereco')
            
            if user.is_aluno:
                perfil.matricula = request.POST.get('matricula')
                perfil.curso = request.POST.get('curso')
                perfil.nome_pai = request.POST.get('nome_pai')
                perfil.nome_mae = request.POST.get('nome_mae')
            elif user.is_professor:
                perfil.siape = request.POST.get('siape')
                perfil.departamento = request.POST.get('departamento')
            
            perfil.save()
            
            # Sincroniza nome com o modelo User
            user.first_name = novo_nome
            user.save()
            
            messages.success(request, "SUCCESS_SYNC: Perfil atualizado com sucesso.")
            return redirect('meu_perfil')
        
        elif 'btn_change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Mantém logado após trocar senha
                messages.success(request, "PASS_SECURED: Senha alterada com sucesso.")
                return redirect('meu_perfil')
            else:
                password_mode = True # Mantém no formulário de senha se houver erro

    return render(request, 'users/meu_perfil.html', {
        'perfil': perfil,
        'tipo_id': tipo_id,
        'identificador': identificador,
        'edit_mode': edit_mode,
        'password_mode': password_mode,
        'password_form': password_form,
    })

@user_passes_test(admin_only)
def historico_sistema(request):
    """Exibe um log unificado de ações do sistema (Audit Log)."""
    from presence_service.models import Presenca
    from academic.models import Turma, Sala
    
    # Pegando os registros mais recentes de várias tabelas
    user_h = User.history.all()[:30]
    turma_h = Turma.history.all()[:20]
    sala_h = Sala.history.all()[:10]
    
    logs = []
    
    # Processando Histórico de Usuários
    for h in user_h:
        nome = f"{h.first_name} {h.last_name}".strip() or h.username
        tipo_acao = "CRIADO" if h.history_type == "+" else "ALTERADO" if h.history_type == "~" else "REMOVIDO"
        logs.append({
            'data': h.history_date,
            'tipo': 'USUÁRIO',
            'user': h.history_user,
            'msg': f"{tipo_acao}: {nome} ({h.email})"
        })
        
    # Processando Histórico de Turmas
    for h in turma_h:
        tipo_acao = "CRIADA" if h.history_type == "+" else "ALTERADA" if h.history_type == "~" else "ENCERRADA"
        nome_disc = h.disciplina.nome if h.disciplina else "Disciplina Removida"
        logs.append({
            'data': h.history_date,
            'tipo': 'TURMA',
            'user': h.history_user,
            'msg': f"{tipo_acao}: {nome_disc} ({h.semestre})"
        })

    # Processando Histórico de Salas
    for h in sala_h:
        logs.append({
            'data': h.history_date,
            'tipo': 'SALA',
            'user': h.history_user,
            'msg': f"SALA_{h.history_type}: {h.nome} ({h.predio})"
        })
    
    # Ordena por data decrescente
    logs = sorted(logs, key=lambda x: x['data'], reverse=True)[:60]
    
    return render(request, 'users/historico.html', {'logs': logs})


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AccountLoginView(LoginView):
    template_name = 'account/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        nome = self.request.user.first_name or self.request.user.username
        messages.success(self.request, f"Conectado com sucesso como {nome}!")
        return response

@login_required
def configuracoes_usuario(request):
    return render(request, 'users/configuracoes.html', {
        'view_name': 'Configurações',
        'is_settings': True
    })
