from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from classes.models import Aula
from .models import Presenca

def get_client_ip(request):
    """Captura o endereço IP real do usuário."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def registrar_presenca(request):
    if request.method == "POST":
        aula_id = request.POST.get('aula_id')
        token = request.POST.get('token')
        lat_aluno = request.POST.get('latitude')
        lon_aluno = request.POST.get('longitude')

        try:
            aula = Aula.objects.get(id=aula_id)
            
            if not hasattr(request.user, 'perfil_aluno'):
                return render(request, 'classes/resultado.html', {
                    'sucesso': False,
                    'erro': 'Apenas contas de alunos podem registrar presença.'
                })
                
            aluno = request.user.perfil_aluno

            # 1. Validação de Segurança (Token UUID)
            if str(aula.token_qr) != token:
                return render(request, 'classes/resultado.html', {
                    'sucesso': False,
                    'erro': 'QR Code inválido ou expirado.'
                })

            # 2. Validação de Aula Ativa
            if not aula.is_ativa():
                return render(request, 'classes/resultado.html', {
                    'sucesso': False,
                    'erro': 'O tempo desta chamada já expirou.'
                })

            # 3. Registro ou Atualização da Presença
            # Capturamos o IP e salvamos junto com a localização
            user_ip = get_client_ip(request)

            presenca, created = Presenca.objects.get_or_create(
                aluno=aluno,
                aula=aula,
                defaults={
                    'latitude': float(lat_aluno) if lat_aluno else None,
                    'longitude': float(lon_aluno) if lon_aluno else None,
                    'ip_registrado': user_ip
                }
            )

            if not created:
                return render(request, 'classes/resultado.html', {
                    'sucesso': False,
                    'erro': f'Você já registrou presença na aula de {aula.turma.disciplina.nome} hoje.',
                    'aula': aula
                })

            return render(request, 'classes/resultado.html', {
                'sucesso': True,
                'aula': aula
            })

        except Aula.DoesNotExist:
            return render(request, 'classes/resultado.html', {
                'sucesso': False,
                'erro': 'Aula não encontrada no sistema.'
            })
        except Exception as e:
            # Esse bloco capturou o erro do banco
            return render(request, 'classes/resultado.html', {
                'sucesso': False,
                'erro': f'Erro interno: {str(e)}'
            })

    return HttpResponse("Acesso negado.", status=405)