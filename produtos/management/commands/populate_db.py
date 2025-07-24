# produtos/management/commands/populate_db.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from produtos.models import Categoria, Produto, MovimentacaoEstoque
from faker import Faker
import random
from PIL import Image # <--- NOVO IMPORT
from io import BytesIO # <--- JÁ DEVE EXISTIR
from django.core.files import File # Se você usa este, certifique-se que está aqui

import requests # <--- ADICIONE ESTA LINHA AQUI!

class Command(BaseCommand):
    help = 'Populates the database with 100 sample products and categories.'

    def handle(self, *args, **options):
        fake = Faker('pt_BR') # Usar Faker em português do Brasil
        self.stdout.write(self.style.SUCCESS('Iniciando o preenchimento do banco de dados...'))

        # 1. Obter ou Criar um Usuário para o cadastro
        # O ideal é ter um superusuário criado previamente
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                # Fallback: Se não encontrar superusuário, pega o primeiro usuário ou cria um simples
                admin_user = User.objects.first()
                if not admin_user:
                    admin_user = User.objects.create_user('admin_teste', 'admin@example.com', 'admin_password')
                    self.stdout.write(self.style.WARNING('Usuário admin_teste criado para preenchimento. Altere a senha em produção!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao obter/criar usuário: {e}'))
            self.stdout.write(self.style.ERROR('Não foi possível preencher o banco de dados sem um usuário.'))
            return

        # 2. Limpar dados existentes (Opcional, mas útil para recomeçar)
        # Atenção: Isso DELETA TODOS os produtos e categorias! Use com cautela.
        Produto.objects.all().delete()
        Categoria.objects.all().delete()
        MovimentacaoEstoque.objects.all().delete()
        self.stdout.write(self.style.WARNING('Dados existentes de Produto, Categoria e MovimentacaoEstoque foram limpos.'))


        # 3. Criar Categorias
        num_categorias = 10
        categorias = []
        for _ in range(num_categorias):
            # Garante que o nome da categoria seja único
            nome_categoria = fake.unique.word().capitalize() + " " + fake.word().capitalize()
            # Tenta criar a categoria, caso já exista uma com esse nome, ignora
            categoria, created = Categoria.objects.get_or_create(
                nome=nome_categoria,
                defaults={'cadastrado_por': admin_user}
            )
            categorias.append(categoria)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoria "{categoria.nome}" criada.'))
            else:
                self.stdout.write(self.style.WARNING(f'Categoria "{categoria.nome}" já existe. Usando existente.'))
        self.stdout.write(self.style.SUCCESS(f'{len(categorias)} categorias prontas.'))


        # 4. Criar Produtos
        num_produtos = 20 # Número total de produtos a criar
        # --- USAR AS UNIDADES DE MEDIDA DO MODELO ---
        unidades = [choice[0] for choice in Produto.UNIDADE_MEDIDA_CHOICES] # Pega apenas os valores internos ('unidade', 'kg', etc.)
        # --- FIM DO USO DAS UNIDADES DE MEDIDA DO MODELO ---
        for i in range(num_produtos):
            nome_produto = fake.unique.word().capitalize() + " " + fake.word().capitalize() # Gera algo como "Mesa Branca" ou "Cadeira Azul"
            descricao = fake.text(max_nb_chars=200)
            codigo_sku = f'ME-{random.randint(10000, 19999)}'
            categoria_aleatoria = random.choice(categorias)
            preco_custo = round(random.uniform(1.5, 50.0), 2)
            preco_venda = round(preco_custo * random.uniform(1.2, 2.5), 2) # Margem de lucro
            quantidade_estoque = random.randint(1, 200)
            unidade_medida = random.choice(unidades)
            localizacao_estoque = f'Corredor {random.randint(1, 10)}, Prateleira {random.randint(1, 20)}'
            fornecedor = fake.company()
            ativo = random.choice([True, False])
            limite_estoque_minimo = random.randint(1, 10)
            limite_estoque_maximo = random.randint(50, 300)

            image_url = f'https://picsum.photos/id/{random.randint(1, 1000)}/600/600' # Pode ser maior, pois vai redimensionar
            image_filename = f'produto_{codigo_sku}.jpeg' # Altere para .jpeg para consistência
            image_file = None

            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()

                image_content_original = BytesIO(response.content)

                # --- LÓGICA DE REDIMENSIONAMENTO NO POPULATE_DB ---
                img = Image.open(image_content_original)
                max_width = 800
                max_height = 800
                quality = 80

                original_width, original_height = img.size
                if original_width > max_width or original_height > max_height:
                    ratio = min(max_width / original_width, max_height / original_height)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS) # Ou Image.ANTIALIAS

                output = BytesIO()
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(output, format='JPEG', quality=quality)
                output.seek(0)
                # --- FIM DA LÓGICA DE REDIMENSIONAMENTO ---

                image_file = File(output, name=image_filename) # Usa o output redimensionado
                self.stdout.write(self.style.SUCCESS(f'Baixou e redimensionou imagem para {nome_produto}.'))

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.WARNING(f'Não foi possível baixar imagem para {nome_produto}: {e}'))
                image_file = None
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Erro ao redimensionar imagem para {nome_produto}: {e}'))
                image_file = None

            # ... (criação do produto com 'imagem': image_file) ...

            produto, created = Produto.objects.get_or_create(
                codigo_sku=codigo_sku, # Usamos ME como base para get_or_create, pois é unique
                defaults={
                    'nome': nome_produto,
                    'descricao': descricao,
                    'categoria': categoria_aleatoria,
                    'preco_custo': preco_custo,
                    'preco_venda': preco_venda,
                    'quantidade_estoque': quantidade_estoque,
                    'unidade_medida': unidade_medida,
                    'localizacao_estoque': localizacao_estoque,
                    'fornecedor': fornecedor,
                    'ativo': ativo,
                    'limite_estoque_minimo': limite_estoque_minimo,
                    'limite_estoque_maximo': limite_estoque_maximo,
                    'cadastrado_por': admin_user,
                    'imagem': image_file
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Produto "{produto.nome}" (ME: {produto.codigo_sku}) criado.'))
            else:
                self.stdout.write(self.style.WARNING(f'Produto com ME "{produto.codigo_sku}" já existe. Usando existente.'))


        # 5. Criar Algumas Movimentações de Estoque (Opcional)
        # Apenas para alguns produtos
        produtos_para_mov = Produto.objects.order_by('?')[:20] # Pega 20 produtos aleatórios
        for produto in produtos_para_mov:
            #tipo = random.choice(['ENTRADA', 'SAIDA'])
            tipo = 'INICIAL'
            #quantidade = random.randint(1, 50)
            quantidade = produto.quantidade_estoque
            observacao = fake.sentence()

            # Lógica para refletir a movimentação no estoque do produto
            if tipo == 'ENTRADA':
                produto.quantidade_estoque += quantidade
                produto.save()
            elif tipo == 'SAIDA':
                if produto.quantidade_estoque >= quantidade:
                    produto.quantidade_estoque -= quantidade
                    produto.save()
                else:
                    quantidade = produto.quantidade_estoque # Sai o que tiver
                    produto.quantidade_estoque = 0
                    produto.save()
                    self.stdout.write(self.style.WARNING(f'Estoque insuficiente para SAIDA de {produto.nome}. Saindo {quantidade}.'))

            MovimentacaoEstoque.objects.create(
                produto=produto,
                tipo_movimentacao=tipo,
                quantidade=quantidade,
                observacao=observacao,
                responsavel=admin_user
            )
            self.stdout.write(self.style.NOTICE(f'Movimentação de {tipo} para {produto.nome}: {quantidade} unidades.'))


        self.stdout.write(self.style.SUCCESS('Banco de dados preenchido com sucesso!'))