from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import User, Aluno, Professor

class MyUserAdmin(SimpleHistoryAdmin, UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Responsabilidades', {'fields': ('is_professor', 'is_aluno')}),
    )
    list_display = ['username', 'email', 'is_professor', 'is_aluno', 'is_staff']

@admin.register(Aluno)
class AlunoAdmin(SimpleHistoryAdmin):
    list_display = ('matricula', 'nome', 'user')
    
    def save_model(self, request, obj, form, change):
        """Se criar um Aluno, marca a flag no User automaticamente."""
        if not change:
            obj.user.is_aluno = True
            obj.user.save()
        super().save_model(request, obj, form, change)

@admin.register(Professor)
class ProfessorAdmin(SimpleHistoryAdmin):
    list_display = ('nome', 'departamento', 'user')

    def save_model(self, request, obj, form, change):
        """Se criar um Professor, marca a flag no User automaticamente."""
        if not change:
            obj.user.is_professor = True
            obj.user.save()
        super().save_model(request, obj, form, change)

admin.site.register(User, MyUserAdmin)
