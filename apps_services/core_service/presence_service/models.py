import uuid
from django.db import models
from simple_history.models import HistoricalRecords
from users.models import Aluno
from classes.models import Aula

class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='presencas')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='presencas_registradas')
    
    horario_registro = models.DateTimeField(auto_now_add=True)
    ip_registrado = models.GenericIPAddressField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    history = HistoricalRecords()
    status = models.CharField(
        max_length=20,
        choices=[('VALIDA', 'Válida'), ('INVALIDA', 'Inválida')],
        default='VALIDA'
    )

    class Meta:
        unique_together = ('aluno', 'aula')
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'

    def __str__(self):
        return f"{self.aluno.nome} - {self.aula.turma.disciplina.nome}"
