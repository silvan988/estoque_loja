# produtos/models.py
from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    cadastrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='categorias_cadastradas', verbose_name="Cadastrado por")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Produto(models.Model):

     # --- DEFINIÇÃO DAS UNIDADES DE MEDIDA ---
    UNIDADE_MEDIDA_CHOICES = [
        ('unidade(s)', 'Unidade(s)'),
        ('kg(s)', 'Quilograma(s) (kg)'),
        ('litro(s)', 'Litro(s) (L)'),
        ('metro(s)', 'Metro(s) (m)'),
        ('pacote(s)', 'Pacote(s)'),
        ('caixa(s)', 'Caixa(s)'),
        ('par(es)', 'Par(es)'),
        ('rolo(s)', 'Rolo(s)'),
        ('conjunto(s)', 'Conjunto(s)'),
        ('galão(ões)', 'Galão(ões)'),
        ('saco(s)', 'Saco(s)'),
    ]
    # --- FIM DA DEFINIÇÃO ---

    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name="Código SKU")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos', verbose_name="Categoria")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Custo")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")
    quantidade_estoque = models.IntegerField(default=0, verbose_name="Quantidade em Estoque")

    unidade_medida = models.CharField(
        max_length=50,
        choices=UNIDADE_MEDIDA_CHOICES, # <-- Usar as escolhas definidas
        default='unidade',
        verbose_name="Unidade de Medida"
    )
    localizacao_estoque = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localização no Estoque")
    data_entrada = models.DateTimeField(auto_now_add=True, verbose_name="Data de Entrada")
    data_ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    fornecedor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fornecedor Principal")
    ativo = models.BooleanField(default=True, verbose_name="Produto Ativo")
    limite_estoque_minimo = models.IntegerField(default=5, verbose_name="Estoque Mínimo")
    limite_estoque_maximo = models.IntegerField(default=100, verbose_name="Estoque Máximo")
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True, verbose_name="Imagem do Produto")
    cadastrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos_cadastrados', verbose_name="Cadastrado por")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def em_falta(self):
        return self.quantidade_estoque <= self.limite_estoque_minimo

class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTACAO_CHOICES = [
        ('INICIAL', 'Inicial'),
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('AJUSTE', 'Ajuste'),
    ]
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes', verbose_name="Produto")
    tipo_movimentacao = models.CharField(max_length=10, choices=TIPO_MOVIMENTACAO_CHOICES, verbose_name="Tipo de Movimentação")
    quantidade = models.IntegerField(verbose_name="Quantidade")
    data_movimentacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Movimentação")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável")

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_movimentacao']

    def __str__(self):
        return f"{self.tipo_movimentacao} de {self.quantidade} {self.produto.unidade_medida} de {self.produto.nome} em {self.data_movimentacao.strftime('%d/%m/%Y %H:%M')}"