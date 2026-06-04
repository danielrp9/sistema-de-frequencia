from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Presenca
from .tasks import check_student_risk_task

@receiver(post_save, sender=Presenca)
def trigger_risk_check(sender, instance, created, **kwargs):
    """
    Sempre que uma presença válida é registrada, 
    disparamos uma tarefa assíncrona para verificar se o aluno 
    está em risco de reprovação.
    """
    if created and instance.status == 'VALIDA':
        # Dispara o check via Celery para não onerar a requisição do aluno
        check_student_risk_task.delay(instance.aluno.id, instance.aula.turma.id)
