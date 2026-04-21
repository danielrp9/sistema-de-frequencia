from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modelo de usuário personalizado para suportar as permissões
    exigidas: Administradores, Professores e Alunos.
    """ 
    is_professor = models.BooleanField(default=False)
    is_aluno = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_aluno')
    nome = models.CharField(max_length=255)
    matricula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    curso = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.matricula} - {self.nome}"

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_professor')
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return self.nome