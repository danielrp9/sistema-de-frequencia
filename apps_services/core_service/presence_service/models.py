import uuid
from django.db import models
from users.models import Aluno
from classes.models import Aula

class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='presencas')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='presencas_registradas')
    
    data_registro = models.DateTimeField(auto_now_add=True)
    
    # Geolocalização
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    ip_registrado = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ('aluno', 'aula')
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'

    def __str__(self):
        return f"{self.aluno.nome} - {self.aula.turma.disciplina.nome}"