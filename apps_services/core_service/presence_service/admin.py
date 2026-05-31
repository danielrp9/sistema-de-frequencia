from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Presenca

@admin.register(Presenca)
class PresencaAdmin(SimpleHistoryAdmin):
    list_display = ('aluno', 'aula', 'horario_registro', 'ip_registrado')
    
    list_filter = ('horario_registro', 'aula__turma__disciplina')

    search_fields = ('aluno__nome', 'aula__turma__disciplina__nome')
    
    readonly_fields = ('horario_registro', 'latitude', 'longitude', 'ip_registrado')
