import qrcode
import uuid
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import Aula

def visualizar_qr_code(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    if not aula.is_ativa():
        return HttpResponse("A aula está encerrada ou fora do horário permitido.", status=403)
  
    tempo_limite = aula.last_token_update + timedelta(seconds=30)
    if timezone.now() > tempo_limite:
        aula.token_qr = uuid.uuid4()
        aula.last_token_update = timezone.now()
        aula.save()

 
    dados_qr = f"https://sistema.edu/presenca?id={aula.id}&token={aula.token_qr}"
    
    # Configuração do QR Code 
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)

    # Cria a imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salva no buffer para resposta HTTP
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

@login_required
def encerrar_aula(request, aula_id):
    """
    Finaliza a aula manualmente para impedir novos registros de presença.
    """
    aula = get_object_or_404(Aula, pk=aula_id)
    
    is_professor_da_aula = False
    if hasattr(request.user, 'professor'):
        is_professor_da_aula = aula.disciplina.professor_responsavel == request.user.professor
    
    if request.user.is_superuser or is_professor_da_aula:
        aula.encerrada_manualmente = True
        aula.save()
        
    return redirect('dashboard')