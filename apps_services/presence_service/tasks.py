from celery import shared_task
from .models import Presenca
from classes.models import Aula
from users.models import Aluno

@shared_task
def processar_presenca_task(aluno_id, aula_id, ip, lat, lon):
    # Esta função roda de forma assíncrona, fora do ciclo de resposta do usuário
    aluno = Aluno.objects.get(id=aluno_id)
    aula = Aula.objects.get(id=aula_id)
    
    Presenca.objects.create(
        aluno=aluno,
        aula=aula,
        ip_registrado=ip,
        latitude=lat,
        longitude=lon,
        status='VALIDA'
    )
    return f"Presença registrada para {aluno.nome}"