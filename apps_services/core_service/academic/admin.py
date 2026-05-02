from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Department, Course, Sala, Disciplina, Turma

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('name', 'code')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)

@admin.register(Sala)
class SalaAdmin(SimpleHistoryAdmin):
    list_display = ('nome', 'predio', 'latitude', 'longitude', 'raio_permitido')
    search_fields = ('nome', 'predio')

@admin.register(Disciplina)
class DisciplinaAdmin(SimpleHistoryAdmin):
    # Alterado para refletir os campos reais do modelo Disciplina
    list_display = ('codigo', 'nome', 'course', 'carga_horaria_total')
    list_filter = ('course',)
    search_fields = ('nome', 'codigo')

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    # Novo Admin para gerenciar as turmas e matrículas manuais
    list_display = ('disciplina', 'professor', 'semestre', 'ativa')
    list_filter = ('semestre', 'ativa', 'professor')
    filter_horizontal = ('alunos',) # Movemos a matrícula manual para cá
    search_fields = ('disciplina__nome', 'professor__nome')