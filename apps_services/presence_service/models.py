from django.db import models
from users.models import Aluno
from classes.models import Aula

class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE) [cite: 66]
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE) [cite: 67]
    horario_registro = models.DateTimeField(auto_now_add=True) [cite: 68]
    ip_registrado = models.GenericIPAddressField() [cite: 69]
    latitude = models.DecimalField(max_digits=9, decimal_places=6) [cite: 70]
    longitude = models.DecimalField(max_digits=9, decimal_places=6) [cite: 71]
    status = models.CharField(max_length=20, choices=[('VALIDA', 'Válida'), ('INVALIDA', 'Inválida')]) [cite: 72]

    def __str__(self):
        return f"{self.aluno.nome} - {self.aula.disciplina.nome} ({self.status})"