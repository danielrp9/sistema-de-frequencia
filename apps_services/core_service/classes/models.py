import uuid
from django.db import models
from academic.models import Disciplina, Sala
from django.utils import timezone

class Aula(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    
    # Token atual (muda periodicamente)
    token_qr = models.UUIDField(default=uuid.uuid4, unique=True) 
    # Data da última vez que o QR mudou
    last_token_update = models.DateTimeField(auto_now_add=True)
    
    # Encerramento manual
    encerrada_manualmente = models.BooleanField(default=False)

    def is_ativa(self):
        """Verifica se a aula pode receber presenças (Horário + Manual)"""
        agora = timezone.localtime().time()
        # Valida se está dentro do horário e não foi encerrada no botão
        return (not self.encerrada_manualmente and 
                self.horario_inicio <= agora <= self.horario_fim)

    def __str__(self):
        return f"{self.disciplina.nome} - {self.data}"