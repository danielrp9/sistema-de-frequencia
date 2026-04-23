from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .utils import validar_ip_universidade, calcular_distancia
from .models import Presenca
from .tasks import processar_presenca_task
from classes.models import Aula

def registrar_presenca(request):
    if request.method == "POST":
        aula_id = request.POST.get('aula_id')
        token = request.POST.get('token')
        lat_aluno = request.POST.get('latitude')
        lon_aluno = request.POST.get('longitude')
        
     
        aula = get_object_or_404(Aula, id=aula_id)
        ip_cliente = request.META.get('REMOTE_ADDR')

        if not request.user.is_authenticated or not hasattr(request.user, 'perfil_aluno'):
            return render(request, 'erro.html', {'msg': 'Acesso negado. Apenas alunos autenticados podem registrar presença.'})

        if str(aula.token_qr) != token:
            return render(request, 'erro.html', {'msg': 'Token de segurança inválido ou expirado.'})

        # Validar se o aluno já registrou presença (Uso de Cache Redis) 
        cache_key = f"presenca:{aula.id}:{request.user.perfil_aluno.id}"
        if cache.get(cache_key):
            return render(request, 'erro.html', {'msg': 'Você já registrou presença para esta aula.'})
      
        agora = timezone.now().time()
        if not (aula.horario_inicio <= agora <= aula.horario_fim):
            return render(request, 'erro.html', {'msg': 'O horário desta aula já expirou ou ainda não começou.'})

        # Validar Rede da Universidade (IP/NAT) 
        if not validar_ip_universidade(ip_cliente):
            return render(request, 'erro.html', {'msg': 'Presença negada. Você deve estar conectado à rede institucional.'})

        if not lat_aluno or not lon_aluno:
            return render(request, 'erro.html', {'msg': 'A geolocalização é obrigatória para registrar presença.'})
            
        distancia = calcular_distancia(lat_aluno, lon_aluno, aula.sala.latitude, aula.sala.longitude)
        if distancia > aula.sala.raio_permitido: # Raio padrão sugerido: 50m 
            return render(request, 'erro.html', {'msg': f'Você está fora do raio da sala ({int(distancia)}m).'})

        cache.set(cache_key, True, timeout=7200)

        # Enviar evento para Fila (RabbitMQ) para gravação assíncrona no banco 
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