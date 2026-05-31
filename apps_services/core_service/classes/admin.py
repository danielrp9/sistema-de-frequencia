from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Aula

@admin.register(Aula)
class AulaAdmin(SimpleHistoryAdmin):
    list_display = ('get_disciplina_nome', 'data', 'horario_inicio', 'peso_aula', 'encerrada_manualmente')
    list_filter = ('data', 'turma__disciplina', 'encerrada_manualmente')
    
    def get_disciplina_nome(self, obj):
        return obj.turma.disciplina.nome
    get_disciplina_nome.short_description = 'Disciplina'    
