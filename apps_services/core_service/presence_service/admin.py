from django.contrib import admin
from .models import Presenca

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'aula', 'data_registro', 'ip_registrado')
    
    list_filter = ('data_registro', 'aula__turma__disciplina')

    search_fields = ('aluno__nome', 'aula__turma__disciplina__nome')
    
    readonly_fields = ('data_registro', 'latitude', 'longitude', 'ip_registrado')