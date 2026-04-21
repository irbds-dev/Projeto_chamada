from django.shortcuts               import render, redirect, get_object_or_404
from .models                        import Turma, Aluno, Chamada
from django.utils                   import timezone
from django.db.models               import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth            import authenticate, login
from django.contrib                 import messages

# 1. TELA DE SELEÇÃO DE TURMAS
def turmas(request):
    todas_turmas = Turma.objects.all()
    return render(request, 'turmas.html', {'turmas': todas_turmas})


# 2. TELA DE CHAMADA (Professor/Coordenação)
def realizar_chamada(request, id_turma):
    turma = get_object_or_404(Turma, id_turma=id_turma)
    alunos = Aluno.objects.filter(id_turma=turma)
    hoje = timezone.now().date()

    chamadas_existentes = Chamada.objects.filter(id_turma=turma, data__date=hoje)
    ja_existe = chamadas_existentes.exists()

    if request.method == 'POST':
        if ja_existe:
            messages.warning(request, f"A chamada da turma {turma.nome} já foi realizada hoje!")
            return redirect('turmas')

        total_presentes = 0
        total_faltosos = 0

        for aluno in alunos:
            # Verifica se o checkbox foi marcado
            esta_presente = f'presenca_{aluno.id_aluno}' in request.POST
            justificativa = request.POST.get(f'justificativa_{aluno.id_aluno}', '')
            
            # Incrementa os contadores conforme a resposta do formulário
            if esta_presente:
                total_presentes += 1
            else:
                total_faltosos += 1

            Chamada.objects.create(
                id_aluno=aluno,
                id_turma=turma,
                presente=esta_presente,
                justificativa=justificativa,
                data=timezone.now(),
                updated_at=timezone.now()
            )
            
        messages.success(
            request, 
            f"Chamada de {turma.nome} finalizada! ✅ Presentes: {total_presentes} | ❌ Faltas: {total_faltosos}"
        )
        return redirect(request.get_full_path())

    mapa_presenca = {c.id_aluno_id: c for c in chamadas_existentes}
    for aluno in alunos:
        registro = mapa_presenca.get(aluno.id_aluno)
        aluno.status_salvo = registro.presente if registro else False
        aluno.justificativa_salva = registro.justificativa if registro else ""

    return render(request, 'chamada.html', {
        'turma': turma,
        'alunos': alunos,
        'ja_existe': ja_existe,
        'presentes_count': chamadas_existentes.filter(presente=True).count(),
        'faltas_count': chamadas_existentes.filter(presente=False).count(),
    })

# 3. EDITAR CHAMADA
@login_required
def editarChamada(request):
    hoje = timezone.now().date()
    turmas = Turma.objects.all()
 
    nome_filtro = request.GET.get('nome', '')
    turma_filtro = request.GET.get('turma', '')
    pesquisou = bool(nome_filtro or turma_filtro)
    
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
        
        # registro.presente = f'presenca_{id_chamada}' in request.POST
        # registro.justificativa = request.POST.get(f'justificativa_{id_chamada}', '')
        # registro.updated_at = timezone.now()
        # registro.save()
        Chamada.objects.filter(id_chamada=id_chamada).update(
        presente=f'presenca_{id_chamada}' in request.POST,
        justificativa=request.POST.get(f'justificativa_{id_chamada}', ''),
        updated_at=timezone.now()
    )
        return redirect(request.get_full_path())

    return render(request, 'editarChamada.html', {
        'chamadas': chamadas,
        'turmas': turmas,
        'pesquisou': pesquisou # Enviamos essa flag para o template
    })


# 3. TELA DE ANÁLISES (Dashboard BI)
@login_required
def analises(request):
    # Cálculos para os KPIs solicitados
    total_registros = Chamada.objects.count()
    presencas = Chamada.objects.filter(presente=True).count()
    
    taxa_presenca = (presencas / total_registros * 100) if total_registros > 0 else 0
    taxa_falta = 100 - taxa_presenca
    
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
    alunos = Aluno.objects.all().order_by('-data')[:10] 
    turmas = Turma.objects.all()
    return render(request, 'cadastroAluno.html', {'alunos': alunos, 'turmas': turmas})

# 5. CADASTRA TURMA
@login_required
def cadastroTurma(request):
    turmas = Turma.objects.all().order_by('-data')[:10] 
    return render(request, 'cadastroTurma.html', {'turmas': turmas})


@login_required
def controle(request):
    chamadas = Chamada.objects.all().order_by('-data')[:5]
    turmas = Turma.objects.all()
    return render(request, 'controle.html', {'turmas': turmas, 'chamadas': chamadas})

# 7. TELA DE LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('turmas')

    if request.method == 'POST':
        usuario_input = request.POST.get('username')
        senha_input = request.POST.get('password')

        user = authenticate(request, username=usuario_input, password=senha_input)

        if user is not None:
            login(request, user)
            return redirect('turmas')
        else:
            messages.error(request, "Usuário ou senha incorretos.")
    
    return render(request, 'login.html')
