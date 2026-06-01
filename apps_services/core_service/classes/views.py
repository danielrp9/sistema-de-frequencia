import qrcode
import uuid
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta

from .models import Aula
from academic.models import Turma, Sala
from academic.serializers import AlunoRelatorioSerializer
from .serializers import AulaGradeSerializer

@login_required
def registrar_aula(request):
    """
    Cria o registro da aula com validação rigorosa de integridade.
    """
    is_professor = getattr(request.user, 'is_professor', False)
    is_admin = request.user.is_superuser
    
    if not (is_professor or is_admin):
        return redirect('dashboard')
        
    if request.method == "POST":
        turma_id = request.POST.get('turma')
        sala_id = request.POST.get('sala')
        peso_str = request.POST.get('peso_aula')
        
        # VALIDAÇÃO DE SEGURANÇA: Impede o IntegrityError do professor
        if not turma_id or not sala_id or not peso_str:
            messages.error(request, "ERRO_INTEGRITY: Turma, Sala ou Carga Horária não selecionada.")
            return redirect('registrar_aula')

        try:
            peso = int(peso_str)
            if peso <= 0:
                raise ValueError("Carga horária deve ser maior que zero.")
            agora = timezone.localtime()
            
            # Criação do objeto com verificação de existência dos IDs
            Aula.objects.create(
                turma_id=int(turma_id),
                sala_id=int(sala_id),
                peso_aula=peso,
                data=agora.date(),
                horario_inicio=(agora - timedelta(minutes=5)).time(),
                horario_fim=(agora + timedelta(hours=peso)).time()
            )
            messages.success(request, "SESSION_CREATED: Chamada inicializada com sucesso.")
            return redirect('dashboard')
        except (ValueError, TypeError) as e:
            messages.error(request, f"ERRO_DATA: Dados inválidos fornecidos ({e}).")
            return redirect('registrar_aula')

    # Filtro de Turmas
    if request.user.is_superuser:
        minhas_turmas = Turma.objects.filter(ativa=True)
    else:
        minhas_turmas = Turma.objects.filter(professor__user=request.user, ativa=True)

    context = {
        'minhas_turmas': minhas_turmas,
        'salas': Sala.objects.all(),
    }
    
    return render(request, 'classes/form_aula.html', context)

@login_required
def visualizar_qr_code(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if not request.user.is_superuser:
        is_dono_aula = (aula.turma.professor.user == request.user)
        if not is_dono_aula:
            return HttpResponse("Acesso negado: Permissão insuficiente.", status=403)

    if not aula.is_ativa():
        return HttpResponse(f"Chamada expirada.", status=403)
  
    agora = timezone.now()
    if agora > (aula.last_token_update + timedelta(seconds=30)):
        aula.token_qr = uuid.uuid4()
        aula.last_token_update = agora
        aula.save()

    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    url_base = f"{protocol}://{host}"
    
    registrar_url = reverse('registrar_presenca')
    dados_qr = f"{url_base}{registrar_url}?id={aula.id}&token={aula.token_qr}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(dados_qr)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="white")
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

@login_required
def registrar_presenca_camera(request):
    if not getattr(request.user, 'is_aluno', False):
        return redirect('dashboard')
    return render(request, 'classes/camera_scan.html')

@login_required
def encerrar_aula(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    if request.user.is_superuser or (aula.turma.professor.user == request.user):
        aula.encerrada_manualmente = True
        aula.save()
    return redirect('dashboard')

@login_required
def relatorio_presenca_disciplina(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    if not (request.user.is_superuser or (turma.professor.user == request.user)):
        return HttpResponse("Acesso negado.", status=403)

    aulas = Aula.objects.filter(turma=turma).order_by('data')
    colunas_datas = AulaGradeSerializer(aulas, many=True).data
    alunos = turma.alunos.all().order_by('nome')
    serializer = AlunoRelatorioSerializer(
        alunos,
        many=True,
        context={'disciplina': turma.disciplina, 'turma': turma},
    )
    
    return render(request, 'classes/relatorio_disciplina.html', {
        'disciplina': turma.disciplina, # Corrigido para bater com o template
        'turma': turma,
        'colunas_datas': colunas_datas,
        'lista_presenca': serializer.data
    })
