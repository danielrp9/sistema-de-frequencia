from rest_framework import serializers
from .models import Presenca
from classes.models import Aula
from django.utils import timezone

class PresencaSerializer(serializers.Serializer):
    aula_id = serializers.IntegerField()
    token = serializers.UUIDField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    def validate(self, data):
        try:
            aula = Aula.objects.get(id=data['aula_id'])
        except Aula.DoesNotExist:
            raise serializers.ValidationError("Aula não encontrada.")

        # 1. Validação do Token (Garante que não é um print antigo)
        if str(aula.token_qr) != str(data['token']):
            raise serializers.ValidationError("QR Code inválido ou expirado.")

        # 2. Validação de Horário e Encerramento Manual
        if not aula.is_ativa():
            raise serializers.ValidationError("A chamada para esta aula não está ativa.")

        self.context['aula'] = aula
        return data