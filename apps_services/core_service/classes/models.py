import uuid
from django.db import models
from academic.models import Turma, Sala
from django.utils import timezone
from datetime import timedelta

class Aula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='aulas')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    data = models.DateField(default=timezone.now)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    
    # Peso definido pelo professor no momento da criação
    peso_aula = models.PositiveIntegerField(default=2)
    
    token_qr = models.UUIDField(default=uuid.uuid4, unique=True) 
    last_token_update = models.DateTimeField(auto_now_add=True)
    
    # GARANTIA: O default deve ser False. 
    encerrada_manualmente = models.BooleanField(default=False)

    def is_ativa(self):
        """
        Verifica se a aula está ativa. Se encerrada_manualmente for True,
        ela morre na hora.
        """
        if self.encerrada_manualmente:
            return False
            
        agora_dt = timezone.localtime()
        
        # Comparação robusta com margem de segurança de 15 minutos
        inicio_dt = timezone.make_aware(timezone.datetime.combine(self.data, self.horario_inicio))
        fim_dt = timezone.make_aware(timezone.datetime.combine(self.data, self.horario_fim))

        return (inicio_dt - timedelta(minutes=15)) <= agora_dt <= fim_dt

    def __str__(self):
        return f"{self.turma.disciplina.nome} - {self.data} ({self.peso_aula}h)"    