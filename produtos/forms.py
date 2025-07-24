# produtos/forms.py

from django import forms
from .models import Produto, Categoria, MovimentacaoEstoque
from django.core.exceptions import ValidationError
from PIL import Image # <--- NOVO IMPORT
from io import BytesIO # <--- NOVO IMPORT
from django.core.files.uploadedfile import InMemoryUploadedFile # <--- NOVO IMPORT
import sys # <--- NOVO IMPORT para depuração, se necessário

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'codigo_sku', 'categoria', 'preco_custo',
            'preco_venda', 'quantidade_estoque', 'unidade_medida',
            'localizacao_estoque', 'fornecedor', 'ativo',
            'limite_estoque_minimo', 'limite_estoque_maximo',
            'imagem'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        if 'imagem' in self.fields:
            self.fields['imagem'].widget.attrs.pop('class', None)

    # --- NOVO MÉTODO PARA REDIMENSIONAR A IMAGEM ---
    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')

        if imagem:
            # Defina a largura máxima e a altura máxima desejadas
            max_width = 800  # Exemplo: Imagens terão no máximo 800 pixels de largura
            max_height = 800 # Exemplo: Imagens terão no máximo 800 pixels de altura
            quality = 80     # Qualidade de compressão (0-100, 80 é um bom balanço)

            # Só processa se a imagem for um arquivo (não nulo ou vazio)
            if hasattr(imagem, 'read'): # Verifica se é um arquivo lido do upload
                try:
                    # Abre a imagem com Pillow
                    img = Image.open(imagem)

                    # Calcula novas dimensões mantendo a proporção
                    original_width, original_height = img.size
                    
                    if original_width > max_width or original_height > max_height:
                        ratio = min(max_width / original_width, max_height / original_height)
                        new_width = int(original_width * ratio)
                        new_height = int(original_height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS) # Ou Image.ANTIALIAS para Pillow < 9.1.0

                    # Salva a imagem redimensionada em um buffer de memória
                    output = BytesIO()
                    
                    # Tenta adivinhar o formato para salvar (JPEG, PNG, etc.)
                    # Se o formato original for GIF e você precisar manter animação, isso é mais complexo.
                    # Para JPEGs e PNGs, geralmente é seguro converter.
                    if img.mode in ('RGBA', 'P'): # Converter PNGs com transparência para RGB antes de salvar como JPEG
                        img = img.convert('RGB')
                    
                    # Salva como JPEG (pode mudar para PNG dependendo da preferência)
                    img.save(output, format='JPEG', quality=quality)
                    output.seek(0) # Volta ao início do buffer

                    # Substitui a imagem original pela versão redimensionada em memória
                    # Mantém o nome original do arquivo
                    imagem = InMemoryUploadedFile(
                        output,
                        'ImageField',
                        f"{imagem.name.split('.')[0]}.jpeg", # Renomeia para .jpeg se o formato de saída for JPEG
                        'image/jpeg', # Tipo de conteúdo
                        sys.getsizeof(output),
                        None
                    )
                    self.cleaned_data['imagem'] = imagem # Atualiza o cleaned_data

                except Exception as e:
                    # Se houver um erro no redimensionamento, levante uma exceção de validação
                    raise ValidationError(f"Erro ao processar imagem: {e}")
        return imagem
    
    # --- NOVO MÉTODO DE VALIDAÇÃO PARA QUANTIDADE_ESTOQUE ---
    def clean_quantidade_estoque(self):
        quantidade = self.cleaned_data.get('quantidade_estoque')
        if quantidade is not None and quantidade <= 0:
            raise ValidationError("A quantidade em estoque deve ser maior que zero ao criar um produto.")
        return quantidade
    # --- FIM DO NOVO MÉTODO ---

    # ... (restante dos métodos clean_quantidade e clean) ...

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        # Campos que o usuário irá preencher
        fields = ['tipo_movimentacao', 'quantidade', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica a classe 'form-control' para estilização Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade <= 0:
            raise ValidationError("A quantidade da movimentação deve ser um valor positivo.")
        return quantidade