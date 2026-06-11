from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Department, Course, Disciplina, Turma, Sala
from users.models import Professor, Aluno, User 
from classes.models import Aula 
import re

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def gestao_departamentos(request):
    """Lista todos os departamentos e permite criar novos via modal."""
    if request.method == "POST" and 'btn_depto' in request.POST:
        name = request.POST.get('name')
        code = request.POST.get('code')
        Department.objects.create(name=name, code=code)
        return redirect('gestao_departamentos')

    departamentos = Department.objects.all().prefetch_related('courses')
    return render(request, 'academic/gestao_departamentos.html', {
        'departamentos': departamentos
    })

@login_required
@user_passes_test(is_admin)
def detalhes_departamento(request, depto_id):
    """Gerencia Cursos de um departamento."""
    depto = get_object_or_404(Department, id=depto_id)
    
    if request.method == "POST" and 'btn_curso' in request.POST:
        Course.objects.create(name=request.POST.get('name'), department=depto)
        return redirect('detalhes_departamento', depto_id=depto.id)

    return render(request, 'academic/detalhes_departamento.html', {
        'depto': depto,
        'cursos': depto.courses.all()
    })

@login_required
@user_passes_test(is_admin)
def detalhes_curso(request, curso_id):
    """Interface para o Administrador gerenciar as Disciplinas Base de um Curso com busca."""
    curso = get_object_or_404(Course, id=curso_id)
    
    if request.method == "POST" and 'btn_disciplina' in request.POST:
        Disciplina.objects.create(
            nome=request.POST.get('nome'),
            codigo=request.POST.get('codigo'),
            carga_horaria_total=request.POST.get('ch'),
            course=curso
        )
        return redirect('detalhes_curso', curso_id=curso.id)

    search_query = request.GET.get('q', '')
    disciplinas = curso.disciplinas.all().order_by('nome')
    
    if search_query:
        disciplinas = disciplinas.filter(
            models.Q(nome__icontains=search_query) | 
            models.Q(codigo__icontains=search_query)
        )

    return render(request, 'academic/detalhes_curso.html', {
        'curso': curso,
        'disciplinas': disciplinas,
        'search_query': search_query
    })

@login_required
@user_passes_test(is_admin)
def detalhes_disciplina(request, disciplina_id):
    """Interface para gerenciar detalhes da disciplina e professores responsáveis."""
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    
    if request.method == "POST":
        if 'add_professor' in request.POST:
            prof_id = request.POST.get('professor_id')
            prof = get_object_or_404(Professor, id=prof_id)
            disciplina.professores_responsaveis.add(prof)
            messages.success(request, f"Prof. {prof.nome} adicionado à disciplina.")
        elif 'remove_professor' in request.POST:
            prof_id = request.POST.get('professor_id')
            prof = get_object_or_404(Professor, id=prof_id)
            disciplina.professores_responsaveis.remove(prof)
            messages.success(request, f"Prof. {prof.nome} removido da disciplina.")
        return redirect('detalhes_disciplina', disciplina_id=disciplina.id)

    professores_atribuidos = disciplina.professores_responsaveis.all()
    # Professores que ainda não foram atribuídos a esta disciplina
    professores_disponiveis = Professor.objects.exclude(id__in=professores_atribuidos.values_list('id', flat=True))

    return render(request, 'academic/detalhes_disciplina.html', {
        'disciplina': disciplina,
        'professores_atribuidos': professores_atribuidos,
        'professores_disponiveis': professores_disponiveis
    })

@login_required
def abrir_turma(request):
    """Interface para o Professor abrir uma turma (ex: 2026.1)."""
    if not getattr(request.user, 'is_professor', False):
        return redirect('dashboard')

    professor_perfil = get_object_or_404(Professor, user=request.user)

    if request.method == "POST":
        disciplina_id = request.POST.get('disciplina')
        semestre = request.POST.get('semestre')
        
        # Garante que o professor é responsável por esta disciplina base
        disciplina = get_object_or_404(Disciplina, id=disciplina_id, professores_responsaveis=professor_perfil)
        
        Turma.objects.create(
            disciplina=disciplina,
            professor=professor_perfil,
            semestre=semestre,
            ativa=True
        )
        messages.success(request, f"Turma de {disciplina.nome} iniciada com sucesso.")
        return redirect('dashboard')

    # Só exibe disciplinas onde o professor é responsável
    disciplinas_autorizadas = Disciplina.objects.filter(professores_responsaveis=professor_perfil).order_by('nome')

    context = {
        'disciplinas_disponiveis': disciplinas_autorizadas,
    }
    return render(request, 'academic/abrir_turma.html', context)

@login_required
def encerrar_turma(request, turma_id):
    """Move a turma para o histórico (ativa=False), preservando os dados para auditoria."""
    turma = get_object_or_404(Turma, id=turma_id)
    
    if not request.user.is_superuser and turma.professor.user != request.user:
        return redirect('dashboard')
        
    turma.ativa = False
    turma.save()
    messages.success(request, f"CONSOLIDATED: A turma {turma.disciplina.nome} foi encerrada e movida para o histórico.")
    return redirect('dashboard')

from .serializers import AlunoRelatorioSerializer
from classes.serializers import AulaGradeSerializer

from .services import AcademicService

@login_required
def folha_frequencia_turma(request, turma_id):
    """Exibe uma folha de frequência limpa e expansiva para a turma."""
    turma = get_object_or_404(Turma, id=turma_id)
    
    if not request.user.is_superuser and turma.professor.user != request.user:
        return redirect('dashboard')
    
    aulas = Aula.objects.filter(turma=turma).order_by('data', 'horario_inicio')
    colunas_datas = AulaGradeSerializer(aulas, many=True).data
    alunos_qs = turma.alunos.all().order_by('nome')
    
    serializer = AlunoRelatorioSerializer(
        alunos_qs,
        many=True,
        context={'turma': turma},
    )
    
    return render(request, 'academic/folha_frequencia.html', {
        'turma': turma,
        'disciplina': turma.disciplina,
        'colunas_datas': colunas_datas,
        'lista_presenca': serializer.data,
    })

@login_required
def alunos_reprovados_turma(request, turma_id):
    """Exibe uma lista isolada e limpa de alunos reprovados por falta em uma turma."""
    turma = get_object_or_404(Turma, id=turma_id)
    
    if not request.user.is_superuser and turma.professor.user != request.user:
        return redirect('dashboard')
    
    alunos_reprovados = AcademicService.get_failed_students(turma)
    limite = turma.disciplina.carga_horaria_total * 0.25
    
    return render(request, 'academic/lista_reprovados_isolada.html', {
        'turma': turma,
        'alunos_reprovados': alunos_reprovados,
        'limite_faltas': limite
    })

@login_required
def lista_turmas_gestao(request):
    """Lista as turmas do professor especificamente para gestão."""
    if not getattr(request.user, 'is_professor', False):
        return redirect('dashboard')
    
    professor_perfil = get_object_or_404(Professor, user=request.user)
    turmas = Turma.objects.filter(professor=professor_perfil, ativa=True).select_related('disciplina')
    
    return render(request, 'academic/lista_turmas_gestao.html', {
        'turmas': turmas
    })

@login_required
def gerenciar_alunos_disciplina(request, turma_id):
    """Interface unificada de gestão da disciplina para o professor."""
    turma = get_object_or_404(Turma, id=turma_id)
    
    if not request.user.is_superuser and turma.professor.user != request.user:
        return redirect('dashboard')
        
    if request.method == "POST":
        if 'email_list' in request.POST:
            count = AcademicService.provision_students_by_email(request.POST.get('email_list'), turma)
            messages.success(request, f"{count} alunos matriculados com sucesso.")
            return redirect('gerenciar_alunos_disciplina', turma_id=turma.id)

    # Dados para o Relatório e Gráfico
    aulas = Aula.objects.filter(turma=turma).order_by('data', 'horario_inicio')
    colunas_datas = AulaGradeSerializer(aulas, many=True).data
    
    alunos_qs = turma.alunos.all().order_by('nome')
    
    # Serialização completa para filtro posterior se necessário
    serializer = AlunoRelatorioSerializer(
        alunos_qs,
        many=True,
        context={'turma': turma},
    )
    
    lista_presenca = serializer.data
    filtro_reprovados = request.GET.get('filter') == 'reprovados'
    
    if filtro_reprovados:
        limite = turma.disciplina.carga_horaria_total * 0.25
        lista_presenca = [aluno for aluno in lista_presenca if aluno['total_faltas'] > limite]

    # Dados do Gráfico ... (rest of the code same)
    from presence_service.models import Presenca
    ultima_aula = aulas.last()
    alunos_count = alunos_qs.count()
    
    total_presencas = 0
    total_faltas = 0
    legenda_grafico = "Sem aulas registradas"
    
    if ultima_aula:
        total_presencas = Presenca.objects.filter(aula=ultima_aula, status='VALIDA').count()
        total_faltas = max(alunos_count - total_presencas, 0)
        legenda_grafico = f"Última Chamada: {ultima_aula.data.strftime('%d/%m')}"
        if ultima_aula.is_ativa:
            legenda_grafico = f"Chamada em Aberto: {ultima_aula.data.strftime('%d/%m')}"

    chart_data = {
        'labels': ['Compareceram', 'Faltaram'],
        'values': [total_presencas, total_faltas],
        'legenda': legenda_grafico
    }

    limite_faltas = turma.disciplina.carga_horaria_total * 0.25

    context = {
        'turma': turma,
        'disciplina': turma.disciplina,
        'alunos_matriculados': alunos_qs,
        'colunas_datas': colunas_datas,
        'lista_presenca': lista_presenca,
        'chart_data': chart_data,
        'filtro_reprovados': filtro_reprovados,
        'limite_faltas': limite_faltas
    }
    
    return render(request, 'academic/gestao_turma.html', context)

@login_required
def gestao_salas(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    if request.method == "POST":
        nome = request.POST.get('nome')
        predio = request.POST.get('predio')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        raio_permitido = request.POST.get('raio_permitido') or 50

        Sala.objects.create(
            nome=nome,
            predio=predio,
            latitude=latitude,
            longitude=longitude,
            raio_permitido=raio_permitido,
        )
        messages.success(request, "GEOFENCE_ADDED: Sala registrada com sucesso.")
        return redirect('gestao_salas')
    
    context = {
        'salas': Sala.objects.all().order_by('nome'),
    }
    return render(request, 'academic/gestao_salas.html', context)
