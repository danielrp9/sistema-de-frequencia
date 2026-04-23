from django.db import models
from users.models import Professor
from simple_history.models import HistoricalRecords

# 1. INFRAESTRUTURA FÍSICA
class Sala(models.Model):
    nome = models.CharField(max_length=100)
    predio = models.CharField(max_length=100)
    # Coordenadas para o Geofencing (Essencial para a Etapa 2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    raio_permitido = models.FloatField(default=50.0) 
    
    history = HistoricalRecords() 

    def __str__(self):
        return f"{self.nome} - {self.predio}"

# 2. HIERARQUIA ADMINISTRATIVA (Organização da UFVJM)
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True) # Ex: DECOM

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name

# 3. O CONTEÚDO (O que é ensinado)
class Disciplina(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=20, unique=True)
    # Vinculamos a disciplina a um curso para ficar organizado 
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='disciplinas')
    
    professor_responsavel = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='disciplinas')
    
    semestre = models.CharField(max_length=10)
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.codigo} - {self.nome}"