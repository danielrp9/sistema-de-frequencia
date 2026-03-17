import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Aula

def visualizar_qr_code(request, aula_id):
    # Obtém os dados da aula [cite: 57]
    aula = get_object_or_404(Aula, pk=aula_id)
    
    # Estrutura o link conforme o exemplo do professor [cite: 82]
    # Substitua 'sistema.edu' pelo IP do seu servidor se necessário
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