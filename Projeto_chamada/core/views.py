from django.shortcuts import render, redirect, get_object_or_404
from .models import Turma, Aluno, Chamada
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required

# 1. TELA DE SELEÇÃO DE TURMAS
def turmas(request):
    todas_turmas = Turma.objects.all()
    return render(request, 'turmas.html', {'turmas': todas_turmas})

# 2. TELA DE CHAMADA (Professor/Coordenação)
def realizar_chamada(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    alunos = Aluno.objects.filter(id_turma=turma)
    
    if request.method == 'POST':
        for aluno in alunos:
            status = f'presenca_{aluno.id_aluno}' in request.POST
            justificativa = request.POST.get(f'justificativa_{aluno.id_aluno}', '')

            # Salva no seu modelo Chamada
            Chamada.objects.create(
                id_turma=turma,
                id_aluno=aluno,
                presente=status,
                justificativa=justificativa,
                data=timezone.now(),
                updated_at=timezone.now()
            )
        return redirect('turmas')

    return render(request, 'chamada.html', {'turma': turma, 'alunos': alunos})

# 3. TELA DE ANÁLISES (Dashboard BI)
@login_required
def analises(request):
    # Cálculos para os KPIs solicitados
    total_registros = Chamada.objects.count()
    presencas = Chamada.objects.filter(presente=True).count()
    
    taxa_presenca = (presencas / total_registros * 100) if total_registros > 0 else 0
    taxa_falta = 100 - taxa_presenca
    
    # Exemplo de Alunos em Risco (> 25% de faltas)
    # Esta é uma lógica simplificada para o Dashboard
    alunos_risco = Aluno.objects.annotate(
        total_faltas=Count('chamada', filter=Q(chamada__presente=False))
    ).filter(total_faltas__gt=5).count()

    context = {
        'taxa_presenca': round(taxa_presenca, 1),
        'taxa_falta': round(taxa_falta, 1),
        'alunos_risco': alunos_risco,
    }
    return render(request, 'analises.html', context)

# 4. TELA DE GESTÃO DE CADASTROS
@login_required
def cadastroAluno(request):
    alunos = Aluno.objects.all().order_by('-data')[:10] # Últimos 10
    turmas = Turma.objects.all()
    return render(request, 'cadastroAluno.html', {'alunos': alunos, 'turmas': turmas})

@login_required
def cadastroTurma(request):
    turmas = Turma.objects.all().order_by('-data')[:10] # Últimos 10
    return render(request, 'cadastroTurma.html', {'turmas': turmas})

@login_required
def controle(request):
    chamadas = Chamada.objects.all().order_by('-data')[:5]
    turmas = Turma.objects.all()
    return render(request, 'controle.html', {'turmas': turmas, 'chamadas': chamadas})

# 5. TELA DE LOGIN
def login_view(request):
    return render(request, 'login.html')

# 6. EDITAR CHAMADA
@login_required
def editarChamada(request):
    hoje = timezone.now().date()
    turmas = Turma.objects.all()
    
    # Captura os filtros
    nome_filtro = request.GET.get('nome', '')
    turma_filtro = request.GET.get('turma', '')

    # Define se houve uma intenção de pesquisa
    pesquisou = bool(nome_filtro or turma_filtro)
    
    # Se não pesquisou, retornamos uma QuerySet vazia (.none())
    if pesquisou:
        chamadas = Chamada.objects.filter(data__date=hoje).select_related('id_aluno', 'id_turma')
        
        if nome_filtro:
            chamadas = chamadas.filter(id_aluno__nome__icontains=nome_filtro)
        if turma_filtro:
            chamadas = chamadas.filter(id_turma_id=turma_filtro)
    else:
        chamadas = Chamada.objects.none()

    if request.method == 'POST':
        id_chamada = request.POST.get('id_chamada')
        registro = get_object_or_404(Chamada, id_chamada=id_chamada)
        
        registro.presente = f'presenca_{id_chamada}' in request.POST
        registro.justificativa = request.POST.get(f'justificativa_{id_chamada}', '')
        registro.updated_at = timezone.now()
        registro.save()
        
        # Mantém os filtros após o POST
        return redirect(request.get_full_path())

    return render(request, 'editarChamada.html', {
        'chamadas': chamadas,
        'turmas': turmas,
        'pesquisou': pesquisou # Enviamos essa flag para o template
    })