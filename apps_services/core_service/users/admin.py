from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Professor, Aluno

@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Status de Perfil', {'fields': ('is_professor', 'is_aluno')}),
    )
    list_display = ('username', 'email', 'is_professor', 'is_aluno', 'is_staff')

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'departamento')

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricula', 'curso')