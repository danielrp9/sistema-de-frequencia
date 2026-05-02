from django.contrib import admin
from .models import Presenca

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    # CORREÇÃO: Removido 'status' e adicionado campos reais do modelo
    list_display = ('aluno', 'aula', 'data_registro', 'ip_registrado')
    
    # Filtros laterais baseados na data e na aula
    list_filter = ('data_registro', 'aula__turma__disciplina')
    
    # Campo de busca para encontrar alunos ou disciplinas rapidamente
    search_fields = ('aluno__nome', 'aula__turma__disciplina__nome')
    
    # Organiza a exibição para leitura apenas no Admin para evitar fraudes manuais
    readonly_fields = ('data_registro', 'latitude', 'longitude', 'ip_registrado')