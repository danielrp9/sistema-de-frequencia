from django.db import models
from users.models import Aluno
from classes.models import Aula

class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE) 
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    horario_registro = models.DateTimeField(auto_now_add=True) 
    ip_registrado = models.GenericIPAddressField() 
    latitude = models.DecimalField(max_digits=9, decimal_places=6) 
    longitude = models.DecimalField(max_digits=9, decimal_places=6) 
    status = models.CharField(max_length=20, choices=[('VALIDA', 'Válida'), ('INVALIDA', 'Inválida')]) 

    def __str__(self):
        return f"{self.aluno.nome} - {self.aula.disciplina.nome} ({self.status})"