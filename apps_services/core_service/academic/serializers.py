from rest_framework import serializers
from .models import Disciplina, Aluno, Turma
from presence_service.models import Presenca
from classes.models import Aula
from django.db.models import Sum

class DisciplinaResumoSerializer(serializers.ModelSerializer):
    """Retorna o resumo da disciplina com cálculos de horas-aula para o painel do aluno."""
    horas_presenca = serializers.SerializerMethodField()
    horas_falta = serializers.SerializerMethodField()
    limite_faltas = serializers.SerializerMethodField()
    porcentagem_frequencia = serializers.SerializerMethodField()

    class Meta:
        model = Disciplina
        fields = [
            'id', 'codigo', 'nome', 'carga_horaria_total',
            'horas_presenca', 'horas_falta', 'limite_faltas', 'porcentagem_frequencia'
        ]

    def get_horas_presenca(self, obj):
        aluno = self.context.get('aluno')
        if not aluno: return 0
        return Presenca.objects.filter(
            aluno=aluno, 
            aula__turma__disciplina=obj,
            status='VALIDA'
        ).aggregate(total=Sum('aula__peso_aula'))['total'] or 0

    def get_horas_falta(self, obj):
        aluno = self.context.get('aluno')
        turma = Turma.objects.filter(disciplina=obj, alunos=aluno).first()
        if not turma: return 0
        
        total_ministrado = Aula.objects.filter(turma=turma).aggregate(
            total=Sum('peso_aula'))['total'] or 0
            
        return total_ministrado - self.get_horas_presenca(obj)

    def get_limite_faltas(self, obj):
        # 25% da carga horária institucional definida pelo Admin
        return obj.carga_horaria_total * 0.25

    def get_porcentagem_frequencia(self, obj):
        aluno = self.context.get('aluno')
        turma = Turma.objects.filter(disciplina=obj, alunos=aluno).first()
        if not turma: return 0

        total_ministrado = Aula.objects.filter(turma=turma).aggregate(
            total=Sum('peso_aula'))['total'] or 0
        
        if total_ministrado == 0: return 100.0
        return round((self.get_horas_presenca(obj) / total_ministrado) * 100, 1)

class AlunoRelatorioSerializer(serializers.ModelSerializer):
    """Retorna os dados do aluno para a grade de presença do professor."""
    grade_presenca = serializers.SerializerMethodField()
    total_faltas = serializers.SerializerMethodField()

    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'matricula', 'grade_presenca', 'total_faltas']

    def get_grade_presenca(self, obj):
        turma = self.context.get('turma')
        aulas = Aula.objects.filter(turma=turma).order_by('data', 'horario_inicio')
        
        grade = []
        for aula in aulas:
            presente = Presenca.objects.filter(aluno=obj, aula=aula, status='VALIDA').exists()
            grade.append({
                'data': aula.data.strftime('%d/%m'),
                'presente': presente,
                'peso': aula.peso_aula
            })
        return grade

    def get_total_faltas(self, obj):
        turma = self.context.get('turma')
        # Pega todas as aulas da turma
        aulas = Aula.objects.filter(turma=turma)
        # IDs das aulas onde o aluno esteve presente
        aulas_presente_ids = Presenca.objects.filter(
            aluno=obj, 
            aula__turma=turma, 
            status='VALIDA'
        ).values_list('aula_id', flat=True)
        
        # Soma o peso das aulas onde o aluno NÃO esteve presente
        total_horas_falta = aulas.exclude(id__in=aulas_presente_ids).aggregate(
            total=Sum('peso_aula')
        )['total'] or 0
        
        return total_horas_falta
