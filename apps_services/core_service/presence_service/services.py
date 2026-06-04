from django.db.models import Sum
from .models import Presenca
from classes.models import Aula

class PresenceService:
    @staticmethod
    def get_student_attendance_stats(aluno, turma):
        """
        Calcula estatísticas de presença de um aluno em uma turma específica.
        Retorna (horas_presenca, horas_falta, frequencia_porcentagem).
        """
        # Horas onde o aluno esteve presente
        horas_presenca = Presenca.objects.filter(
            aluno=aluno, 
            aula__turma=turma,
            status='VALIDA'
        ).aggregate(total=Sum('aula__peso_aula'))['total'] or 0
        
        # Total de horas ministradas até o momento para esta turma
        total_ministrado = Aula.objects.filter(turma=turma).aggregate(
            total=Sum('peso_aula'))['total'] or 0
            
        horas_falta = total_ministrado - horas_presenca
        
        porcentagem = 100.0
        if total_ministrado > 0:
            porcentagem = round((horas_presenca / total_ministrado) * 100, 1)
            
        return horas_presenca, horas_falta, porcentagem

    @staticmethod
    def is_student_present(aluno, aula):
        """Verifica se um aluno esteve presente em uma aula específica."""
        return Presenca.objects.filter(aluno=aluno, aula=aula, status='VALIDA').exists()

    @staticmethod
    def get_total_absences(aluno, turma):
        """Retorna o total de horas de falta de um aluno em uma turma."""
        aulas = Aula.objects.filter(turma=turma)
        aulas_presente_ids = Presenca.objects.filter(
            aluno=aluno, 
            aula__turma=turma, 
            status='VALIDA'
        ).values_list('aula_id', flat=True)
        
        return aulas.exclude(id__in=aulas_presente_ids).aggregate(
            total=Sum('peso_aula')
        )['total'] or 0
