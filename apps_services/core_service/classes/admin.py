from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Aula

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    # 'data' deve ser o nome exato que está no seu models.py (vimos que você usou 'data')
    list_display = ('disciplina', 'data', 'horario_inicio', 'horario_fim', 'link_qr_code')
    list_filter = ('data', 'disciplina')

    def link_qr_code(self, obj):
        # Certifique-se de que o 'name' na sua urls.py é 'visualizar_qr_code'
        url = reverse('visualizar_qr_code', args=[obj.id])
        return format_html('<a href="{}" target="_blank" style="text-decoration:none;"> Gerar QR Code</a>', url)
    
    link_qr_code.short_description = 'QR Code'