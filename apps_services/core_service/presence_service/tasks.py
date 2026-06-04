import logging

from celery import shared_task
from django.db import IntegrityError, transaction

from classes.models import Aula
from users.models import Aluno
from .models import Presenca

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def processar_presenca_task(self, aluno_id, aula_id, ip, lat, lon):
    aluno = Aluno.objects.get(id=aluno_id)
    aula = Aula.objects.get(id=aula_id)

    try:
        with transaction.atomic():
            presenca, created = Presenca.objects.get_or_create(
                aluno=aluno,
                aula=aula,
                defaults={
                    'ip_registrado': ip,
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'status': 'VALIDA',
                },
            )
    except (IntegrityError, ValueError) as exc:
        logger.warning("Presenca duplicada ou invalida no Celery: %s", exc)
        return {
            'sucesso': False,
            'codigo': 'PRESENCA_DUPLICADA',
            'mensagem': 'Presenca ja existente ou dados invalidos.',
            'aula_id': aula_id,
            'aluno_id': aluno_id,
        }

    if created:
        logger.info("Presenca %s criada via fila Celery.", presenca.id)
        return {
            'sucesso': True,
            'codigo': 'PRESENCA_PROCESSADA',
            'presenca_id': presenca.id,
            'aula_id': aula.id,
            'aluno_id': aluno.id,
        }

    return {
        'sucesso': True,
        'codigo': 'PRESENCA_JA_EXISTENTE',
        'presenca_id': presenca.id,
        'aula_id': aula.id,
        'aluno_id': aluno.id,
    }


@shared_task
def check_student_risk_task(aluno_id, turma_id):
    """
    Tarefa assíncrona que verifica se um aluno específico atingiu 
    o limite de faltas em uma turma e gera notificações.
    """
    from users.models import Aluno
    from academic.models import Turma
    from users.services import NotificationService
    
    try:
        aluno = Aluno.objects.get(id=aluno_id)
        turma = Turma.objects.get(id=turma_id)
        
        # Chama o serviço de notificação para processar esse aluno específico
        NotificationService.sync_student_notifications(aluno.user)
        
        # Também podemos avisar o professor se o aluno reprovou
        NotificationService.sync_professor_notifications(turma.professor.user)
        
    except Exception as e:
        logger.error(f"Erro ao processar check de risco: {e}")
