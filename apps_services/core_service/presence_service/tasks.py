from celery import shared_task
from .models import Presenca
from classes.models import Aula
from users.models import Aluno
import logging

logger = logging.getLogger(__name__)

@shared_task
def processar_presenca_task(aluno_id, aula_id, ip, lat, lon):
    try:
        aluno = Aluno.objects.get(id=aluno_id)
        aula = Aula.objects.get(id=aula_id)
        
        # Garantimos que a presença seja criada com o status que o serializer do relatório busca
        Presenca.objects.create(
            aluno=aluno,
            aula=aula,
            ip_registrado=ip,
            latitude=lat,
            longitude=lon,
            status='VALIDA' # Deve ser idêntico ao filtro do AlunoRelatorioSerializer
        )
        return f"Sucesso: {aluno.nome} registrado na aula {aula.id}"
    except Exception as e:
        logger.error(f"Erro no Celery: {str(e)}")
        return f"Falha: {str(e)}"