from rest_framework import serializers
from .models import Aula

class AulaGradeSerializer(serializers.ModelSerializer):
    """Retorna as datas das aulas para o cabeçalho do relatório."""
    data_formatada = serializers.SerializerMethodField()

    class Meta:
        model = Aula
        fields = ['id', 'data', 'data_formatada']

    def get_data_formatada(self, obj):
        return obj.data.strftime('%d/%m')