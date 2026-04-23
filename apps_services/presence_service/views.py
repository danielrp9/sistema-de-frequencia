from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .utils import validar_ip_universidade, calcular_distancia
from .models import Presenca
from .tasks import processar_presenca_task
from classes.models import Aula

def registrar_presenca(request):
    """
    View responsável por validar os requisitos de rede, localização e token,
    enviando o registro para processamento assíncrono via Celery.
    """
    if request.method == "POST":
        aula_id = request.POST.get('aula_id')
        token = request.POST.get('token')
        lat_aluno = request.POST.get('latitude')
        lon_aluno = request.POST.get('longitude')
        
        # Busca a aula e extrai o IP do cliente 
        aula = get_object_or_404(Aula, id=aula_id)
        ip_cliente = request.META.get('REMOTE_ADDR')

        # 1. Validar autenticação do aluno 
        if not request.user.is_authenticated or not hasattr(request.user, 'perfil_aluno'):
            return render(request, 'erro.html', {'msg': 'Acesso negado. Apenas alunos autenticados podem registrar presença.'})

        # 2. Validar Token do QR Code 
        if str(aula.token_qr) != token:
            return render(request, 'erro.html', {'msg': 'Token de segurança inválido ou expirado.'})

        # 3. Validar se o aluno já registrou presença (Uso de Cache Redis) 
        cache_key = f"presenca:{aula.id}:{request.user.perfil_aluno.id}"
        if cache.get(cache_key):
            return render(request, 'erro.html', {'msg': 'Você já registrou presença para esta aula.'})

        # 4. Validar Horário da Aula 
        agora = timezone.now().time()
        if not (aula.horario_inicio <= agora <= aula.horario_fim):
            return render(request, 'erro.html', {'msg': 'O horário desta aula já expirou ou ainda não começou.'})

        # 5. Validar Rede da Universidade (IP/NAT) 
        if not validar_ip_universidade(ip_cliente):
            return render(request, 'erro.html', {'msg': 'Presença negada. Você deve estar conectado à rede institucional.'})

        # 6. Validar Geolocalização (Raio permitido da sala) 
        if not lat_aluno or not lon_aluno:
            return render(request, 'erro.html', {'msg': 'A geolocalização é obrigatória para registrar presença.'})
            
        distancia = calcular_distancia(lat_aluno, lon_aluno, aula.sala.latitude, aula.sala.longitude)
        if distancia > aula.sala.raio_permitido: # Raio padrão sugerido: 50m 
            return render(request, 'erro.html', {'msg': f'Você está fora do raio da sala ({int(distancia)}m).'})

        # 7. Marcar no Cache Redis antes de enviar para a fila (Evita concorrência) 
        # Expira em 2 horas para garantir que o aluno não registre novamente na mesma aula
        cache.set(cache_key, True, timeout=7200)

        # 8. Enviar evento para Fila (RabbitMQ) para gravação assíncrona no banco 
        processar_presenca_task.delay(
            aluno_id=request.user.perfil_aluno.id,
            aula_id=aula.id,
            ip=ip_cliente,
            lat=lat_aluno,
            lon=lon_aluno
        )

        return render(request, 'sucesso.html', {
            'msg': 'Sua presença está sendo processada e será registrada em instantes.'
        })

    context = {
        'aula_id': request.GET.get('id'),
        'token': request.GET.get('token')
    }
    return render(request, 'registrar_presenca.html', context)