import uuid
from django.db import models
from academic.models import Disciplina, Sala

class Aula(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    token_qr = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 

    def __str__(self):
        return f"{self.disciplina.nome} - {self.data}"