import qrcode
import uuid
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from .models import Aula
from academic.models import Turma, Sala
from academic.serializers import AlunoRelatorioSerializer
from .serializers import AulaGradeSerializer

@login_required
def registrar_aula(request):
    """
    Cria o registro da aula e redireciona ao Dashboard.
    A aula agora é gerenciada através de um card de controle no Dashboard.
    """
    is_professor = getattr(request.user, 'is_professor', False)
    is_admin = request.user.is_superuser
    
    if not (is_professor or is_admin):
        return redirect('dashboard')
        
    if request.method == "POST":
        turma_id = request.POST.get('turma')
        sala_id = request.POST.get('sala')
        peso = int(request.POST.get('peso_aula', 2))
        
        agora = timezone.localtime()
        
        # Cria a aula com o horário de início 5 minutos antes para garantir ativação imediata
        # O redirecionamento para o dashboard impede a criação de duplicatas ao dar F5
        Aula.objects.create(
            turma_id=turma_id,
            sala_id=sala_id,
            peso_aula=peso,
            data=agora.date(),
            horario_inicio=(agora - timedelta(minutes=5)).time(),
            horario_fim=(agora + timedelta(hours=peso)).time()
        )
        return redirect('dashboard')

    # Administrador vê todas as turmas, professor vê apenas as suas
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
    """Gera o token dinâmico do QR Code para uma aula existente. Não cria novos registros."""
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if not request.user.is_superuser:
        is_dono_aula = (aula.turma.professor.user == request.user)
        if not is_dono_aula:
            return HttpResponse("Acesso negado: Você não tem permissão para esta chamada.", status=403)

    if not aula.is_ativa():
        return HttpResponse(f"Chamada inativa. (Horário: {aula.horario_inicio} - {aula.horario_fim})", status=403)
  
    agora = timezone.now()
    if agora > (aula.last_token_update + timedelta(seconds=30)):
        aula.token_qr = uuid.uuid4()
        aula.last_token_update = agora
        aula.save()

    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    url_base = f"{protocol}://{host}"
    
    dados_qr = f"{url_base}/presence/registrar/?id={aula.id}&token={aula.token_qr}"
    
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
    is_autorizado = request.user.is_superuser or (aula.turma.professor.user == request.user)
    if is_autorizado:
        aula.encerrada_manualmente = True
        aula.save()
    return redirect('dashboard')

@login_required
def relatorio_presenca_disciplina(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    is_autorizado = request.user.is_superuser or (turma.professor.user == request.user)
    if not is_autorizado:
        return HttpResponse("Acesso negado.", status=403)

    aulas = Aula.objects.filter(turma=turma).order_by('data')
    colunas_datas = AulaGradeSerializer(aulas, many=True).data
    alunos = turma.alunos.all().order_by('nome')
    serializer = AlunoRelatorioSerializer(alunos, many=True, context={'disciplina': turma.disciplina})
    
    return render(request, 'classes/relatorio_disciplina.html', {
        'turma': turma,
        'colunas_datas': colunas_datas,
        'lista_presenca': serializer.data
    })