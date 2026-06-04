from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

class User(AbstractUser):
    """
    Modelo de usuário personalizado para suportar as permissões
    exigidas: Administradores, Professores e Alunos.
    """ 
    THEME_CHOICES = [
        ('default', 'Padrão (Futurista)'),
        ('light', 'Claro'),
        ('dark', 'Escuro'),
    ]

    is_professor = models.BooleanField(default=False)
    is_aluno = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    # Novas preferências de usuário
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='default')

    history = HistoricalRecords()

    def get_short_name(self):
        """Retorna apenas o primeiro nome para evitar quebra de layout."""
        name = self.first_name or self.username
        return name.split()[0] if name else ""

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_aluno')
    nome = models.CharField(max_length=255)
    matricula = models.CharField(max_length=11, unique=True) # Aumentado/Garantido para 11
    email = models.EmailField(unique=True)
    curso = models.CharField(max_length=100)
    
    # Novos campos biográficos
    telefone = models.CharField(max_length=20, null=True, blank=True)
    nome_pai = models.CharField(max_length=255, null=True, blank=True)
    nome_mae = models.CharField(max_length=255, null=True, blank=True)
    endereco = models.TextField(null=True, blank=True)
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.matricula} - {self.nome}"

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_professor')
    nome = models.CharField(max_length=255)
    siape = models.CharField(max_length=7, unique=True, null=True, blank=True) # Novo campo SIAPE
    email = models.EmailField(unique=True)
    departamento = models.CharField(max_length=100)
    
    # Novos campos de contato
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.TextField(null=True, blank=True)
    
    history = HistoricalRecords()

    def __str__(self):
        return self.nome

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes_usuario')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=20, default='info') # info, warning, danger
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
