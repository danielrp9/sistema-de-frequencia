from rest_framework import serializers
from .models import Disciplina, Aluno, Turma
from presence_service.services import PresenceService
from classes.models import Aula

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
        turma = Turma.objects.filter(disciplina=obj, alunos=aluno).first()
        if not (aluno and turma): return 0
        h_pres, _, _ = PresenceService.get_student_attendance_stats(aluno, turma)
        return h_pres

    def get_horas_falta(self, obj):
        aluno = self.context.get('aluno')
        turma = Turma.objects.filter(disciplina=obj, alunos=aluno).first()
        if not (aluno and turma): return 0
        _, h_falta, _ = PresenceService.get_student_attendance_stats(aluno, turma)
        return h_falta

    def get_limite_faltas(self, obj):
        return obj.carga_horaria_total * 0.25

    def get_porcentagem_frequencia(self, obj):
        aluno = self.context.get('aluno')
        turma = Turma.objects.filter(disciplina=obj, alunos=aluno).first()
        if not (aluno and turma): return 100.0
        _, _, perc = PresenceService.get_student_attendance_stats(aluno, turma)
        return perc

class AlunoRelatorioSerializer(serializers.ModelSerializer):
    """Retorna os dados do aluno para a grade de presença do professor."""
    nome = serializers.SerializerMethodField()
    grade_presenca = serializers.SerializerMethodField()
    total_faltas = serializers.SerializerMethodField()

    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'matricula', 'grade_presenca', 'total_faltas']

    def get_nome(self, obj):
        return obj.user.get_full_name() or obj.nome or obj.user.username

    def get_grade_presenca(self, obj):
        turma = self.context.get('turma')
        aulas = Aula.objects.filter(turma=turma).order_by('data', 'horario_inicio')
        
        grade = []
        for aula in aulas:
            presente = PresenceService.is_student_present(obj, aula)
            grade.append({
                'data': aula.data.strftime('%d/%m'),
                'presente': presente,
                'peso': aula.peso_aula
            })
        return grade

    def get_total_faltas(self, obj):
        turma = self.context.get('turma')
        return PresenceService.get_total_absences(obj, turma)
