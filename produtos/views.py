# produtos/views.py
# produtos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, MovimentacaoEstoque
from .forms import ProdutoForm, CategoriaForm, MovimentacaoEstoqueForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys

@login_required
def lista_produtos(request):
    produtos_list = Produto.objects.all()

    # Lógica de Busca (Já implementada, só confirmando)
    query = request.GET.get('q') # Pega o termo de busca da URL (ex: ?q=camiseta)
    if query:
        produtos_list = produtos_list.filter(
            Q(nome__icontains=query) |
            Q(descricao__icontains=query) |
            Q(codigo_sku__icontains=query) |
            Q(fornecedor__icontains=query) |
            Q(categoria__nome__icontains=query)
        ).distinct() # .distinct() para evitar duplicatas se um produto tiver várias correspondências

    # Lógica de Paginação (Já implementada)
    paginator = Paginator(produtos_list, 10) # 10 produtos por página
    page = request.GET.get('page')
    try:
        produtos = paginator.page(page)
    except PageNotAnInteger:
        produtos = paginator.page(1)
    except EmptyPage:
        produtos = paginator.page(paginator.num_pages)

    # Passa o termo de busca (query) para o template para que ele possa ser preenchido no campo de busca
    return render(request, 'produtos/lista_produtos.html', {'produtos': produtos, 'query': query})

# ... (restante das suas views) ...

@login_required
def detalhe_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    # --- ADICIONE ESTA LINHA PARA BUSCAR AS MOVIMENTAÇÕES ---
    movimentacoes = produto.movimentacoes.all().order_by('-data_movimentacao') # Ordena da mais recente para a mais antiga
    # --- FIM DA ADIÇÃO ---
    return render(request, 'produtos/detalhe_produto.html', {
        'produto': produto,
        'movimentacoes': movimentacoes # <--- PASSE AS MOVIMENTAÇÕES PARA O TEMPLATE
    })

@login_required
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.cadastrado_por = request.user
            produto.quantidade_inicial = produto.quantidade_estoque # Mantém a quantidade inicial no campo do produto
            produto.save() # Salva o produto primeiro para ter um PK

            # --- CRIAR MOVIMENTAÇÃO INICIAL ---
            if produto.quantidade_estoque > 0: # Só cria se a quantidade inicial for maior que zero
                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo_movimentacao='INICIAL',
                    quantidade=produto.quantidade_estoque,
                    observacao='Estoque inicial no cadastro do produto.',
                    responsavel=request.user
                )
                messages.success(request, f'Movimentação inicial de {produto.quantidade_estoque} unidades registrada para {produto.nome}.')
            # --- FIM DA CRIAÇÃO DA MOVIMENTAÇÃO INICIAL ---

            messages.success(request, 'Produto criado com sucesso!')
            return redirect('detalhe_produto', pk=produto.pk)
        else:
            messages.error(request, 'Erro ao criar produto. Por favor, corrija os erros do formulário.')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/criar_editar_produto.html', {'form': form, 'titulo': 'Adicionar Novo Produto'})

@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        # --- PONTO CRÍTICO: PASSAR request.FILES AQUI ---
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            produto.save() # Se 'cadastrado_por' não é editado, save() direto funciona
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('detalhe_produto', pk=produto.pk)
        else:
            # Se o formulário for inválido na edição, mostre os erros
            messages.error(request, 'Erro ao atualizar produto. Por favor, corrija os erros do formulário.')
    else:
        form = ProdutoForm(instance=produto) # Ao carregar o formulário, preenche com dados existentes
    return render(request, 'produtos/criar_editar_produto.html', {'form': form, 'titulo': f'Editar Produto: {produto.nome}'})

@login_required
def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        messages.info(request, 'Produto removido com sucesso!')
        return redirect('lista_produtos')
    return render(request, 'produtos/confirmar_delecao.html', {'produto': produto})

# Views para Categoria (opcional, mas recomendado)
@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('lista_produtos') # Ou uma página de lista de categorias
    else:
        form = CategoriaForm()
    return render(request, 'produtos/criar_editar_categoria.html', {'form': form, 'titulo': 'Criar Nova Categoria'})

@login_required
def lista_categorias(request):
    categorias_list = Categoria.objects.all()

    # Lógica de Busca para Categorias
    query = request.GET.get('q') # Pega o termo de busca
    if query:
        categorias_list = categorias_list.filter(
            Q(nome__icontains=query) # Filtra pelo nome da categoria
        )

    # Não precisamos de paginação para 10 categorias, mas se tiver muitas, considere adicionar
    paginator = Paginator(categorias_list, 10)
    page = request.GET.get('page')
    try:
        categorias = paginator.page(page)
    except PageNotAnInteger:
        categorias = paginator.page(1)
    except EmptyPage:
        categorias = paginator.page(paginator.num_pages)

    return render(request, 'produtos/lista_categorias.html', {'categorias': categorias, 'query': query}) # Passa o 'query'


@login_required # Garante que apenas usuários logados podem acessar
def movimentar_estoque(request, pk):
    produto = get_object_or_404(Produto, pk=pk) # Busca o produto que será movimentado
    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False) # Não salva ainda, vamos adicionar mais dados
            movimentacao.produto = produto # Associa a movimentação ao produto
            movimentacao.responsavel = request.user # Associa a movimentação ao usuário logado

            tipo_movimentacao = movimentacao.tipo_movimentacao
            quantidade = movimentacao.quantidade

            if tipo_movimentacao == 'ENTRADA':
                produto.quantidade_estoque += quantidade
                messages.success(request, f'Entrada de {quantidade} unidades registrada para {produto.nome}.')
            elif tipo_movimentacao == 'SAIDA':
                if produto.quantidade_estoque >= quantidade:
                    produto.quantidade_estoque -= quantidade
                    messages.success(request, f'Saída de {quantidade} unidades registrada para {produto.nome}.')
                else:
                    # Se não há estoque suficiente para a saída, exibe um erro
                    messages.error(request, f'Erro: Não há estoque suficiente para registrar a saída de {quantidade} unidades de {produto.nome}. Estoque atual: {produto.quantidade_estoque}.')
                    # Não redireciona, mostra o formulário novamente com a mensagem de erro
                    return render(request, 'produtos/movimentar_estoque.html', {'form': form, 'produto': produto})
            elif tipo_movimentacao == 'AJUSTE':
                # Para AJUSTE, a lógica aqui é mais de feedback e instrução,
                # pois o campo "quantidade" no formulário de ajuste não é tão intuitivo
                # para uma alteração direta (poderia ser + ou -).
                # Se for um ajuste pontual (ex: inventário), a edição direta do produto é mais fácil.
                messages.warning(request, 'Ajustes de estoque podem ser complexos. Considere usar Entrada/Saída ou ajustar a quantidade diretamente na edição do produto para ajustes pontuais.')
                messages.info(request, 'Para um ajuste simples, adicione ou subtraia manualmente a quantidade no campo "Quantidade em Estoque" na edição do produto.')
                return redirect('detalhe_produto', pk=produto.pk) # Redireciona sem salvar a movimentação de ajuste complexa

            produto.save() # Salva a nova quantidade do produto
            movimentacao.save() # Salva o registro da movimentação no histórico
            return redirect('detalhe_produto', pk=produto.pk) # Redireciona para os detalhes do produto

        else:
            # Se o formulário for inválido (ex: quantidade negativa), exibe os erros
            messages.error(request, 'Erro ao registrar movimentação. Por favor, corrija os erros do formulário.')
    else:
        # Se for uma requisição GET, exibe o formulário vazio
        form = MovimentacaoEstoqueForm()
    return render(request, 'produtos/movimentar_estoque.html', {'form': form, 'produto': produto})
