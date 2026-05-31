from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import PresencaSerializer
from .tasks import processar_presenca_task


def _get_presenca_lock_key(aluno, aula):
    return f"presenca_lock:{aluno.id}:{aula.id}"


def _acquire_presenca_lock(aluno, aula):
    timeout = getattr(settings, 'PRESENCA_DUPLICATE_LOCK_TIMEOUT', 60)
    return cache.add(_get_presenca_lock_key(aluno, aula), True, timeout)


def _release_presenca_lock(aluno, aula):
    cache.delete(_get_presenca_lock_key(aluno, aula))


def _format_serializer_error(errors):
    if not errors:
        return "Erro desconhecido."

    if isinstance(errors, dict):
        for value in errors.values():
            if isinstance(value, list):
                return str(value[0])
            if isinstance(value, dict):
                return _format_serializer_error(value)
            return str(value)

    if isinstance(errors, list):
        return str(errors[0])

    return str(errors)


def _api_error_response(message, http_status, code='VALIDATION_ERROR', errors=None):
    payload = {
        'sucesso': False,
        'codigo': code,
        'mensagem': message,
    }
    if errors is not None:
        payload['erros'] = errors
    return Response(payload, status=http_status)


def _api_success_response(aula, task_id=None, http_status=status.HTTP_202_ACCEPTED):
    return Response({
        'sucesso': True,
        'codigo': 'PRESENCA_ENFILEIRADA',
        'mensagem': 'Presenca validada e enviada para processamento.',
        'dados': {
            'aula_id': aula.id,
            'disciplina': aula.turma.disciplina.nome,
            'turma_id': aula.turma.id,
            'sala': aula.sala.nome,
            'task_id': task_id,
        },
    }, status=http_status)


def _enfileirar_processamento(aluno, aula, user_ip, lat_aluno, lon_aluno):
    return processar_presenca_task.apply_async(
        args=[aluno.id, aula.id, user_ip, lat_aluno, lon_aluno],
        countdown=0,
    )


@login_required
def registrar_presenca(request):
    if request.method != "POST":
        return HttpResponse("Acesso negado.", status=405)

    serializer = PresencaSerializer(data=request.POST, context={'request': request})
    if not serializer.is_valid():
        erro = _format_serializer_error(serializer.errors)
        aula = serializer.context.get('aula')
        return render(request, "classes/resultado.html", {
            "sucesso": False,
            "erro": erro,
            "aula": aula,
        })

    aula = serializer.context['aula']
    aluno = serializer.context['aluno']
    user_ip = serializer.context['user_ip']
    lat_aluno = serializer.validated_data['latitude']
    lon_aluno = serializer.validated_data['longitude']

    if not _acquire_presenca_lock(aluno, aula):
        return render(request, "classes/resultado.html", {
            "sucesso": False,
            "erro": "Registro ja enviado. Aguarde alguns instantes antes de tentar novamente.",
            "aula": aula,
        })

    try:
        _enfileirar_processamento(aluno, aula, user_ip, lat_aluno, lon_aluno)
    except Exception:
        _release_presenca_lock(aluno, aula)
        return render(request, "classes/resultado.html", {
            "sucesso": False,
            "erro": "Fila indisponivel. Tente novamente em instantes.",
            "aula": aula,
        })

    return render(request, "classes/resultado.html", {
        "sucesso": True,
        "aula": aula,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_presenca_api(request):
    serializer = PresencaSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        return _api_error_response(
            _format_serializer_error(serializer.errors),
            status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors,
        )

    aula = serializer.context['aula']
    aluno = serializer.context['aluno']
    user_ip = serializer.context['user_ip']
    lat_aluno = serializer.validated_data['latitude']
    lon_aluno = serializer.validated_data['longitude']

    if not _acquire_presenca_lock(aluno, aula):
        return _api_error_response(
            "Registro ja enviado. Aguarde alguns instantes antes de tentar novamente.",
            status.HTTP_409_CONFLICT,
            code='PRESENCA_EM_PROCESSAMENTO',
        )

    try:
        task_result = _enfileirar_processamento(aluno, aula, user_ip, lat_aluno, lon_aluno)
    except Exception:
        _release_presenca_lock(aluno, aula)
        return _api_error_response(
            "Fila de processamento indisponivel. Tente novamente em instantes.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
            code='FILA_INDISPONIVEL',
        )

    return _api_success_response(aula, task_id=task_result.id)
