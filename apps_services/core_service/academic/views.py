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
    """Gerencia Cursos e visualiza todos os Professores cadastrados no sistema."""
    depto = get_object_or_404(Department, id=depto_id)
    
    if request.method == "POST" and 'btn_curso' in request.POST:
        Course.objects.create(name=request.POST.get('name'), department=depto)
        return redirect('detalhes_departamento', depto_id=depto.id)

    todos_professores = User.objects.filter(is_professor=True).order_by('first_name')

    return render(request, 'academic/detalhes_departamento.html', {
        'depto': depto,
        'cursos': depto.courses.all(),
        'todos_professores': todos_professores
    })

@login_required
@user_passes_test(is_admin)
def detalhes_curso(request, curso_id):
    """Interface para o Administrador gerenciar as Disciplinas Base de um Curso."""
    curso = get_object_or_404(Course, id=curso_id)
    
    if request.method == "POST" and 'btn_disciplina' in request.POST:
        Disciplina.objects.create(
            nome=request.POST.get('nome'),
            codigo=request.POST.get('codigo'),
            carga_horaria_total=request.POST.get('ch'),
            course=curso
        )
        return redirect('detalhes_curso', curso_id=curso.id)

    disciplinas = curso.disciplinas.all().order_by('nome')
    return render(request, 'academic/detalhes_curso.html', {
        'curso': curso,
        'disciplinas': disciplinas
    })

@login_required
def abrir_turma(request):
    """Interface para o Professor abrir uma turma (ex: 2026.1)."""
    if not getattr(request.user, 'is_professor', False):
        return redirect('dashboard')

    if request.method == "POST":
        disciplina_id = request.POST.get('disciplina')
        semestre = request.POST.get('semestre')
        professor_perfil = get_object_or_404(Professor, user=request.user)
        
        Turma.objects.create(
            disciplina_id=disciplina_id,
            professor=professor_perfil,
            semestre=semestre,
            ativa=True
        )
        return redirect('dashboard')

    context = {
        'disciplinas_disponiveis': Disciplina.objects.all().order_by('nome'),
    }
    return render(request, 'academic/abrir_turma.html', context)

from .serializers import AlunoRelatorioSerializer
from classes.serializers import AulaGradeSerializer

@login_required
def gerenciar_alunos_disciplina(request, turma_id):
    """Interface unificada de gestão da disciplina para o professor."""
    turma = get_object_or_404(Turma, id=turma_id)
    
    if not request.user.is_superuser and turma.professor.user != request.user:
        return redirect('dashboard')
        
    if request.method == "POST":
        if 'email_list' in request.POST:
            raw_emails = request.POST.get('email_list')
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_emails)
            emails = [e.lower() for e in emails]
            
            alunos_encontrados = Aluno.objects.filter(email__in=emails)
            for aluno in alunos_encontrados:
                turma.alunos.add(aluno)
            
            messages.success(request, f"{alunos_encontrados.count()} alunos matriculados com sucesso.")
            return redirect('gerenciar_alunos_disciplina', turma_id=turma.id)

    # Dados para o Relatório e Gráfico
    aulas = Aula.objects.filter(turma=turma).order_by('data', 'horario_inicio')
    colunas_datas = AulaGradeSerializer(aulas, many=True).data
    
    alunos_qs = turma.alunos.all().order_by('nome')
    serializer = AlunoRelatorioSerializer(
        alunos_qs,
        many=True,
        context={'turma': turma},
    )

    # Dados do Gráfico (Focado na última atividade: aula ativa ou última realizada)
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
        if ultima_aula.is_ativa():
            legenda_grafico = f"Chamada em Aberto: {ultima_aula.data.strftime('%d/%m')}"

    chart_data = {
        'labels': ['Compareceram', 'Faltaram'],
        'values': [total_presencas, total_faltas],
        'legenda': legenda_grafico
    }

    context = {
        'turma': turma,
        'disciplina': turma.disciplina,
        'alunos_matriculados': alunos_qs,
        'colunas_datas': colunas_datas,
        'lista_presenca': serializer.data,
        'chart_data': chart_data
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
