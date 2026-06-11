from rest_framework import serializers
from .models import Presenca
from classes.models import Aula
from .utils import get_client_ip, validar_ip_universidade, validar_geolocalizacao

class PresencaSerializer(serializers.Serializer):
    aula_id = serializers.IntegerField()
    token = serializers.UUIDField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    def validate(self, data):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError("Request context é obrigatório.")

        user = request.user
        if not user.is_authenticated:
            raise serializers.ValidationError("Autenticação necessária.")

        if not hasattr(user, 'perfil_aluno'):
            raise serializers.ValidationError("Apenas contas de alunos podem registrar presença.")

        try:
            aula = Aula.objects.select_related('sala', 'turma', 'turma__disciplina').get(id=data['aula_id'])
        except Aula.DoesNotExist:
            raise serializers.ValidationError("Aula não encontrada.")

        if str(aula.token_qr) != str(data['token']):
            raise serializers.ValidationError("QR Code inválido ou expirado.")

        if not aula.is_ativa:
            raise serializers.ValidationError("A chamada para esta aula não está ativa.")

        aluno = user.perfil_aluno
        if not aula.turma.alunos.filter(id=aluno.id).exists():
            raise serializers.ValidationError("Você não está matriculado nesta turma.")

        if Presenca.objects.filter(aluno=aluno, aula=aula).exists():
            raise serializers.ValidationError("Você já registrou presença nesta aula.")

        user_ip = get_client_ip(request)
        if not validar_ip_universidade(user_ip):
            raise serializers.ValidationError(
                f"Presença negada. Seu IP ({user_ip}) não pertence à rede permitida."
            )

        try:
            dentro_do_raio, distancia = validar_geolocalizacao(
                data['latitude'], data['longitude'], aula.sala
            )
        except ValueError:
            raise serializers.ValidationError("Localização inválida recebida pelo sistema.")

        if not dentro_do_raio:
            raise serializers.ValidationError(
                f"Presença negada. Você está a aproximadamente {distancia:.2f} metros da sala, "
                f"mas o limite permitido é {aula.sala.raio_permitido:.2f} metros."
            )

        self.context['aula'] = aula
        self.context['aluno'] = aluno
        self.context['user_ip'] = user_ip
        return data