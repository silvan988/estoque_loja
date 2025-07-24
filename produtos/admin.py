# produtos/admin.py
from django.contrib import admin
from .models import Categoria, Produto, MovimentacaoEstoque
from django.db.models import F # Para usar F() expressions

# Filtro personalizado para "Em Falta"
class EmFaltaFilter(admin.SimpleListFilter):
    title = ('status de estoque')
    parameter_name = 'em_falta'

    def lookups(self, request, model_admin):
        return (
            ('sim', 'Sim'),
            ('nao', 'Não'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'sim':
            return queryset.filter(quantidade_estoque__lte=F('limite_estoque_minimo'))
        if self.value() == 'nao':
            return queryset.filter(quantidade_estoque__gt=F('limite_estoque_minimo'))
        return queryset

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cadastrado_por')
    search_fields = ('nome',)
    readonly_fields = ('cadastrado_por',) # Torna o campo somente leitura no Admin

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo_sku', 'categoria', 'quantidade_estoque', 'preco_venda', 'ativo', 'em_falta', 'cadastrado_por')
    list_filter = ('categoria', 'ativo', EmFaltaFilter, 'cadastrado_por') # Adicionei o filtro personalizado e cadastrado_por
    search_fields = ('nome', 'codigo_sku', 'descricao', 'fornecedor')
    list_editable = ('preco_venda', 'quantidade_estoque', 'ativo')
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'codigo_sku', 'categoria', 'fornecedor', 'unidade_medida', 'localizacao_estoque', 'imagem')
        }),
        ('Informações de Preço e Estoque', {
            'fields': ('preco_custo', 'preco_venda', 'quantidade_estoque', 'limite_estoque_minimo', 'limite_estoque_maximo')
        }),
        ('Status', {
            'fields': ('ativo',),
            'classes': ('collapse',)
        }),
        ('Registro', {
            'fields': ('cadastrado_por',),
            'classes': ('collapse',),
            'description': 'Informações de registro do produto.'
        }),
    )
    readonly_fields = ('cadastrado_por',) # Torna o campo somente leitura no Admin
    date_hierarchy = 'data_entrada'
    actions = ['marcar_inativo', 'marcar_ativo']

    def marcar_inativo(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, "Produtos marcados como inativos com sucesso.")
    marcar_inativo.short_description = "Marcar produtos selecionados como inativos"

    def marcar_ativo(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, "Produtos marcados como ativos com sucesso.")
    marcar_ativo.short_description = "Marcar produtos selecionados como ativos"

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo_movimentacao', 'quantidade', 'data_movimentacao', 'responsavel')
    list_filter = ('tipo_movimentacao', 'data_movimentacao', 'responsavel')
    search_fields = ('produto__nome', 'observacao')
    readonly_fields = ('data_movimentacao', 'responsavel') # Não permite edição manual desses campos
    