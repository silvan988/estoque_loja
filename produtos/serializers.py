# produtos/serializers.py
from rest_framework import serializers
from .models import Produto, Categoria, MovimentacaoEstoque
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CategoriaSerializer(serializers.ModelSerializer):
    cadastrado_por = UserSerializer(read_only=True)
    cadastrado_por_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='cadastrado_por', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'cadastrado_por', 'cadastrado_por_id']

class ProdutoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )
    cadastrado_por = UserSerializer(read_only=True) # Campo para exibir o usuário
    cadastrado_por_id = serializers.PrimaryKeyRelatedField( # Campo para receber o ID do usuário (se necessário criar/editar via API)
        queryset=User.objects.all(), source='cadastrado_por', write_only=True, required=False, allow_null=True
    )


    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'descricao', 'codigo_sku', 'categoria', 'categoria_id',
            'preco_custo', 'preco_venda', 'quantidade_estoque', 'unidade_medida',
            'localizacao_estoque', 'data_entrada', 'data_ultima_atualizacao',
            'fornecedor', 'ativo', 'limite_estoque_minimo', 'limite_estoque_maximo',
            'imagem', 'em_falta', 'cadastrado_por', 'cadastrado_por_id'
        ]
        read_only_fields = ['data_entrada', 'data_ultima_atualizacao', 'em_falta']

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    responsavel = UserSerializer(read_only=True) # Exibe detalhes do responsável
    responsavel_id = serializers.PrimaryKeyRelatedField( # Permite passar o ID do responsável
        queryset=User.objects.all(), source='responsavel', write_only=True, required=False, allow_null=True
    )
    produto_nome = serializers.CharField(source='produto.nome', read_only=True) # Adiciona o nome do produto

    class Meta:
        model = MovimentacaoEstoque
        fields = ['id', 'produto', 'produto_nome', 'tipo_movimentacao', 'quantidade', 'data_movimentacao', 'observacao', 'responsavel', 'responsavel_id']
        read_only_fields = ['data_movimentacao'] # 'responsavel' é preenchido automaticamente, mas pode ser enviado o ID