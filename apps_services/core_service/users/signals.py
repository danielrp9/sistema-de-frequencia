from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Aluno, Professor

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria o perfil (Aluno/Professor) automaticamente ao criar o User.
    Isso garante que o Dashboard encontre o 'perfil_aluno' ou 'perfil_professor'.
    """
    if created:
        nome_completo = instance.first_name or instance.get_full_name() or instance.username
        if instance.is_aluno:
            Aluno.objects.get_or_create(
                user=instance,
                defaults={
                    'nome': nome_completo,
                    'email': instance.email,
                    'matricula': f"MAT-{instance.id:04d}",
                    'curso': 'Não Definido'
                }
            )
        elif instance.is_professor:
            Professor.objects.get_or_create(
                user=instance,
                defaults={
                    'nome': nome_completo,
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
