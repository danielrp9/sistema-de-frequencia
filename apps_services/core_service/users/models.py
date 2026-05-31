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
    is_professor = models.BooleanField(default=False)
    is_aluno = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_aluno')
    nome = models.CharField(max_length=255)
    matricula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    curso = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        # Retorna Matrícula e Nome para facilitar a busca no filter_horizontal do Admin
        return f"{self.matricula} - {self.nome}"

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_professor')
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    departamento = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome

# --- SIGNALS PARA AUTOMAÇÃO DE PERFIL ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria o perfil (Aluno/Professor) automaticamente ao criar o User.
    Isso garante que o Dashboard encontre o 'perfil_aluno' ou 'perfil_professor'.
    """
    if created:
        if instance.is_aluno:
            Aluno.objects.get_or_create(
                user=instance,
                defaults={
                    'nome': instance.get_full_name() or instance.username,
                    'email': instance.email,
                    'matricula': f"MAT-{instance.id:04d}",
                    'curso': 'Não Definido'
                }
            )
        elif instance.is_professor:
            Professor.objects.get_or_create(
                user=instance,
                defaults={
                    'nome': instance.get_full_name() or instance.username,
                    'email': instance.email,
                    'departamento': 'Geral'
                }
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sincroniza as atualizações do User com o Perfil correspondente."""
    if instance.is_aluno and hasattr(instance, 'perfil_aluno'):
        instance.perfil_aluno.save()
    if instance.is_professor and hasattr(instance, 'perfil_professor'):
        instance.perfil_professor.save()
