from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Department, Course, Sala, Disciplina

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
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
    list_display = ('codigo', 'nome', 'professor_responsavel', 'course', 'semestre')
    list_filter = ('semestre', 'course')
    search_fields = ('nome', 'codigo')