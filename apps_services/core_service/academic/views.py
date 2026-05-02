from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Department, Course, Disciplina, Turma
from users.models import Professor, Aluno, User 
# CORREÇÃO: Importando Aula do app correto (classes)
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

@login_required
def gerenciar_alunos_disciplina(request, turma_id):
    """Interface para matrícula em lote de alunos via e-mail."""
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
            
            return redirect('gerenciar_alunos_disciplina', turma_id=turma.id)

        return redirect('dashboard')

    matriculados = turma.alunos.all().order_by('nome')
    return render(request, 'academic/gestao_turma.html', {
        'turma': turma,
        'alunos_matriculados': matriculados
    })