from django.shortcuts               import render, redirect, get_object_or_404
from .models                        import Turma, Aluno, Chamada
from django.utils                   import timezone
from django.db.models               import Count, Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth            import authenticate, login
from django.contrib                 import messages
from django.http                    import JsonResponse


# 1. TELA DE SELEÇÃO DE TURMAS
@login_required
def turmas(request):
    termo_busca = request.GET.get('nm_turma', '').strip()
    
    if termo_busca:
        todas_turmas = Turma.objects.filter(nome__icontains=termo_busca)
    else:
        todas_turmas = Turma.objects.all()

    return render(request, 'turmas.html', {
        'turmas': todas_turmas,
        'termo_busca': termo_busca
    })


# 2. TELA DE CHAMADA (Professor/Coordenação)
@login_required
@permission_required('core.add_chamada', raise_exception=True)
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
            esta_presente = f'presenca_{aluno.id_aluno}' in request.POST
            justificativa = request.POST.get(f'justificativa_{aluno.id_aluno}', '')
            
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
@permission_required('core.change_chamada', raise_exception=True)
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
        
        Chamada.objects.filter(id_chamada=id_chamada).update(
        presente=f'presenca_{id_chamada}' in request.POST,
        justificativa=request.POST.get(f'justificativa_{id_chamada}', ''),
        updated_at=timezone.now()
    )
        return redirect(request.get_full_path())

    return render(request, 'editarChamada.html', {
        'chamadas': chamadas,
        'turmas': turmas,
        'pesquisou': pesquisou
    })

# =====================================================================
# 4. TELA DE ANÁLISES (Dashboard BI)
# =====================================================================
@login_required
@permission_required('core.view_chamada', raise_exception=True)
def analises(request):
    turmas_disponiveis = Turma.objects.values_list('nome', flat=True).distinct().order_by('nome')
    periodos_disponiveis = Turma.objects.values_list('periodo', flat=True).distinct().order_by('periodo')
    
    # Busca dinamicamente a primeira chamada registrada no banco de dados para iniciar os filtros nela
    try:
        primeira_chamada = Chamada.objects.earliest('data')
        data_inicial_filtro = primeira_chamada.data.strftime('%Y-%m-%d')
        ano_inicial_filtro = primeira_chamada.data.year
        mes_inicial_filtro = primeira_chamada.data.month
    except Chamada.DoesNotExist:
        # Fallback caso o banco esteja completamente vazio
        data_inicial_filtro = timezone.now().strftime('%Y-%m-%d')
        ano_inicial_filtro = timezone.now().year
        mes_inicial_filtro = ""

    context = {
        'turmas_disponiveis': turmas_disponiveis,
        'periodos_disponiveis': periodos_disponiveis,
        'data_inicial': data_inicial_filtro,
        'ano_inicial': ano_inicial_filtro,
        'mes_inicial': mes_inicial_filtro
    }
    return render(request, 'analises.html', context)


@login_required
def dados_dashboard(request):
    # 1. Filtros Globais recebidos via AJAX
    filtro_ano = request.GET.get('ano')
    filtro_mes = request.GET.get('mes')
    filtro_turma = request.GET.get('turma')
    filtro_periodo = request.GET.get('periodo')
    filtro_aluno = request.GET.get('aluno')
    filtro_data = request.GET.get('data')

    # Se nenhum filtro veio e existem registros, define o ponto de partida do banco de dados
    if not any([filtro_ano, filtro_mes, filtro_turma, filtro_periodo, filtro_aluno, filtro_data]):
        try:
            primeira = Chamada.objects.earliest('data')
            filtro_ano = str(primeira.data.year)
            filtro_mes = str(primeira.data.month)
            filtro_data = primeira.data.strftime('%Y-%m-%d')
        except Chamada.DoesNotExist:
            pass

    # Querysets Base
    chamadas_qs = Chamada.objects.select_related('id_aluno', 'id_turma').all()
    alunos_qs = Aluno.objects.all()

    # 2. Aplicação Estrita dos Filtros Dinâmicos
    if filtro_ano:
        chamadas_qs = chamadas_qs.filter(data__year=filtro_ano)
    if filtro_mes:
        chamadas_qs = chamadas_qs.filter(data__month=filtro_mes)
    if filtro_turma:
        chamadas_qs = chamadas_qs.filter(id_turma__nome=filtro_turma)
        alunos_qs = alunos_qs.filter(id_turma__nome=filtro_turma)
    if filtro_periodo:
        chamadas_qs = chamadas_qs.filter(id_turma__periodo=filtro_periodo)
        alunos_qs = alunos_qs.filter(id_turma__periodo=filtro_periodo)
    if filtro_aluno:
        chamadas_qs = chamadas_qs.filter(id_aluno__nome__icontains=filtro_aluno)
        alunos_qs = alunos_qs.filter(nome__icontains=filtro_aluno)
    if filtro_data:
        chamadas_qs = chamadas_qs.filter(data__date=filtro_data)

    # 3. Métricas Gerais (KPIs)
    total_alunos_cadastrados = alunos_qs.count()
    total_registros_chamada = chamadas_qs.count()
    total_presencas = chamadas_qs.filter(presente=True).count()
    total_faltas = chamadas_qs.filter(presente=False).count()
    
    taxa_presenca = round((total_presencas / total_registros_chamada * 100), 1) if total_registros_chamada > 0 else 0
    taxa_falta = round(100 - taxa_presenca, 1) if total_registros_chamada > 0 else 0

    # 4. Evolução Mensal de Presença
    evolucao_mensal = []
    for mes_idx in range(1, 13):
        qs_mes = chamadas_qs.filter(data__month=mes_idx)
        tot_mes = qs_mes.count()
        if tot_mes > 0:
            evolucao_mensal.append(round((qs_mes.filter(presente=True).count() / tot_mes) * 100, 1))
        else:
            evolucao_mensal.append(0)

    # 5. Top 10 Alunos Faltantes
    top_10 = chamadas_qs.filter(presente=False).values(
        'id_aluno__nome', 'id_turma__nome', 'id_turma__periodo'
    ).annotate(total_faltas=Count('id_aluno')).order_by('-total_faltas')[:10]
    
    top_10_list = [{
        'aluno_nome': item['id_aluno__nome'],
        'turma_nome': item['id_turma__nome'],
        'periodo': item['id_turma__periodo'],
        'total_faltas': item['total_faltas']
    } for item in top_10]

    # 6. Distribuição do Funil de Risco
    comportamento = chamadas_qs.values('id_aluno').annotate(faltas=Count('id_aluno', filter=Q(presente=False)))
    alerta = sum(1 for a in comportamento if 3 <= a['faltas'] < 6)
    risco = sum(1 for a in comportamento if 6 <= a['faltas'] < 10)
    critico = sum(1 for a in comportamento if 10 <= a['faltas'] < 15)
    evasao = sum(1 for a in comportamento if a['faltas'] >= 15)

    # 7. Faltas por Turma
    faltas_turma_raw = chamadas_qs.values('id_turma__nome').annotate(
        total=Count('id_aluno'), faltas=Count('id_aluno', filter=Q(presente=False))
    )
    labels_turmas = [t['id_turma__nome'] for t in faltas_turma_raw if t['id_turma__nome']]
    pct_faltas_turmas = [
        round((t['faltas'] / t['total']) * 100, 1) if t['total'] > 0 else 0 for t in faltas_turma_raw if t['id_turma__nome']
    ]

    # 8. Lista Geral de Alunos (Tabela Final)
    # A tabela inferior traz apenas os registros correspondentes ao filtro_data ativo
    tabela_alunos = []
    if filtro_data:
        chamadas_dia = chamadas_qs.filter(data__date=filtro_data)
        for c in chamadas_dia:
            tabela_alunos.append({
                'aluno': c.id_aluno.nome if c.id_aluno else 'N/A',
                'turma': c.id_turma.nome if c.id_turma else 'N/A',
                'periodo': c.id_turma.periodo if c.id_turma else 'N/A',
                'presente': 'Sim' if c.presente else 'Não',
                'justificativa': c.justificativa or ''
            })

    return JsonResponse({
        'taxa_presenca': taxa_presenca,
        'taxa_falta': taxa_falta,
        'total_alunos': total_alunos_cadastrados,
        'alunos_risco': critico + evasao,
        'evolucao_mensal': evolucao_mensal,
        'top_10_faltantes': top_10_list,
        'funil': {'total': total_alunos_cadastrados, 'alerta': alerta, 'risco': risco, 'critico': critico, 'evasao': evasao},
        'labels_turmas': labels_turmas,
        'pct_faltas_turmas': pct_faltas_turmas,
        'tabela_alunos': tabela_alunos
    })

"""
# 5. TELA DE GESTÃO DE CADASTROS
@permission_required('core.add_aluno', raise_exception=True)
@login_required
def cadastroAluno(request):
    alunos = Aluno.objects.all().order_by('-data')[:10] 
    turmas = Turma.objects.all()
    return render(request, 'cadastroAluno.html', {'alunos': alunos, 'turmas': turmas})
"""

# 6. CADASTRA TURMA
@login_required
@permission_required('core.add_turma', raise_exception=True)
def cadastroTurma(request):
    turmas = Turma.objects.all().order_by('-data')

    if request.method == 'POST':
        nome_input = request.POST.get('new_turma')
        Periodo_turma = request.POST.get('Periodo_turma')

        if nome_input and Periodo_turma:
            registro = Turma.objects.filter(nome=nome_input, periodo=Periodo_turma).count()
            if registro == 0:
                Turma.objects.create(
                    nome=nome_input,
                    periodo=Periodo_turma,
                    data=timezone.now(),
                    updated_at=timezone.now()
                )
                messages.success(request, f"Turma {nome_input} cadastrada com sucesso!")
            else:
                messages.error(request, f"Turma {nome_input} já cadastrada anteriormente!")
            return redirect('cadastroTurma')
        else:
            messages.error(request, "Preencha todos os campos corretamente.")

    return render(request, 'cadastroTurma.html', {
        'turmas': turmas
    })

# 7. CADASTRO ALUNO
@login_required
@permission_required('core.add_aluno', raise_exception=True)
def cadastroAluno(request):
    turmas = Turma.objects.all().order_by('nome')
    turma_filtrada_id = request.GET.get('id_turma', '').strip()

    if turma_filtrada_id:
        alunos = Aluno.objects.filter(id_turma_id=turma_filtrada_id).order_by('-nome')
    else:
        # Se nenhuma turma for escolhida, traz os cadastrados recentemente (ex: últimos 10)
        alunos = Aluno.objects.all().order_by('id_turma')[:10]

    if request.method == 'POST':
        nome = request.POST.get('nome')
        id_turma = request.POST.get('id_turma')

        if nome and id_turma:
            Aluno.objects.create(
                nome=nome,
                id_turma_id=id_turma,
                data=timezone.now(),
                updated_at=timezone.now()
            )
            messages.success(request, f"Aluno {nome} cadastrado com sucesso!")
            return redirect('cadastroAluno')
        else:
            messages.error(request, "Preencha todos os campos corretamente.")

    return render(request, 'cadastroAluno.html', {
        'turmas': turmas,
        'alunos': alunos,
        'turma_filtrada_id': turma_filtrada_id
    })

# 8. TELA DE LOGIN
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