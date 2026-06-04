from .models import Aluno, Turma
from presence_service.services import PresenceService
import re

class AcademicService:
    @staticmethod
    def get_failed_students(turma):
        """
        Retorna a lista de alunos que ultrapassaram o limite de 25% de faltas.
        Retorna lista de dicionários com dados resumidos.
        """
        limite = turma.disciplina.carga_horaria_total * 0.25
        reprovados = []
        
        for aluno in turma.alunos.all():
            faltas = PresenceService.get_total_absences(aluno, turma)
            if faltas > limite:
                reprovados.append({
                    'id': aluno.id,
                    'nome': aluno.user.get_full_name() or aluno.nome,
                    'matricula': aluno.matricula,
                    'total_faltas': faltas,
                    'limite': limite
                })
        return reprovados

    @staticmethod
    def provision_students_by_email(email_string, turma):
        """Processa uma string de e-mails e matricula os alunos na turma."""
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email_string)
        emails = [e.lower() for e in emails]
        
        alunos_encontrados = Aluno.objects.filter(email__in=emails)
        for aluno in alunos_encontrados:
            turma.alunos.add(aluno)
            
        return alunos_encontrados.count()
