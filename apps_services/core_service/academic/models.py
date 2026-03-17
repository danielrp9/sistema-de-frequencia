from django.db import models
from users.models import Professor
from simple_history.models import HistoricalRecords

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    predio = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    raio_permitido = models.FloatField(default=50.0)
    
    # Registro de auditoria 
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.nome} - {self.predio}"

class Disciplina(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=20, unique=True)
    professor_responsavel = models.ForeignKey(Professor, on_delete=models.CASCADE)
    semestre = models.CharField(max_length=10)
    
    # Registro de auditoria 
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.codigo} - {self.nome}"