from django.db import models
from users.models import Professor, Aluno
from simple_history.models import HistoricalRecords

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    predio = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    raio_permitido = models.FloatField(default=50.0) 
    history = HistoricalRecords() 

    def __str__(self):
        return f"{self.nome} - {self.predio}"

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.department.code})"

class Disciplina(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='disciplinas')
    # Carga horária total definida pelo Super Admin
    carga_horaria_total = models.PositiveIntegerField(default=60)
    professores_responsaveis = models.ManyToManyField(Professor, related_name='disciplinas_sob_responsabilidade', blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class Turma(models.Model):
    """Instância da disciplina no semestre vinculada ao professor e alunos."""
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='turmas_ativas')
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='minhas_turmas')
    alunos = models.ManyToManyField(Aluno, related_name='turmas_matriculadas', blank=True)
    semestre = models.CharField(max_length=10)
    ativa = models.BooleanField(default=True)
    history = HistoricalRecords(m2m_fields=[alunos])

    def __str__(self):
        return f"{self.disciplina.nome} - {self.professor.nome} ({self.semestre})"
