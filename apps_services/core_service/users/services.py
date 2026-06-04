from academic.models import Turma
from presence_service.services import PresenceService
from .models import Notification
from django.urls import reverse

class NotificationService:
    @staticmethod
    def sync_professor_notifications(user):
        """Sincroniza notificações de alunos reprovados para o professor."""
        if not getattr(user, 'is_professor', False):
            return
            
        minhas_turmas = Turma.objects.filter(professor__user=user, ativa=True).select_related('disciplina')
        for turma in minhas_turmas:
            limite = turma.disciplina.carga_horaria_total * 0.25
            alunos_reprovados = []
            
            for aluno in turma.alunos.all():
                faltas = PresenceService.get_total_absences(aluno, turma)
                if faltas > limite:
                    alunos_reprovados.append(aluno.nome)
            
            if alunos_reprovados:
                link = reverse('alunos_reprovados_turma', args=[turma.id])
                msg = f"Os seguintes alunos atingiram o limite de faltas em {turma.disciplina.nome}: {', '.join(alunos_reprovados[:3])}"
                if not Notification.objects.filter(user=user, link=link, is_read=False).exists():
                    Notification.objects.create(
                        user=user, 
                        title=f"Alunos Reprovados: {turma.disciplina.codigo}",
                        message=msg, 
                        link=link, 
                        type='danger'
                    )

    @staticmethod
    def sync_student_notifications(user):
        """Sincroniza notificações de risco de reprovação para o aluno."""
        if not getattr(user, 'is_aluno', False):
            return
            
        try:
            perfil = user.perfil_aluno
            turmas = Turma.objects.filter(alunos=perfil, ativa=True)
            for t in turmas:
                _, faltas, _ = PresenceService.get_student_attendance_stats(perfil, t)
                if faltas > (t.disciplina.carga_horaria_total * 0.25):
                    msg = f"ALERTA: Você ultrapassou 25% de faltas na disciplina {t.disciplina.nome}."
                    if not Notification.objects.filter(user=user, message=msg, is_read=False).exists():
                        Notification.objects.create(
                            user=user, 
                            title="Reprovação por Falta", 
                            message=msg, 
                            type='danger'
                        )
        except:
            pass
