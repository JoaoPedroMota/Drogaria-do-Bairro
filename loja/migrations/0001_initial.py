# Generated by Django 4.1.7 on 2023-06-19 17:31

from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import loja.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utilizador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nome', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.EmailField(error_messages={'unique': 'Já existe um utilizador com esse e-mail.'}, max_length=200, null=True, unique=True)),
                ('username', models.CharField(error_messages={'unique': 'Já existe um utilizador com esse nome de utilizador.'}, help_text='Máximo 20 caracteres. Apenas letras, números e os seguintes símbolos @/./+/-/_ ', max_length=200, null=True, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()])),
                ('pais', django_countries.fields.CountryField(default='PT', max_length=2, null=True)),
                ('cidade', models.CharField(blank=True, default='', max_length=200)),
                ('freguesia', models.CharField(max_length=200, null=True)),
                ('morada', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('telemovel', phonenumber_field.modelfields.PhoneNumberField(default='', error_messages={'unique': 'Já existe um utilizador com esse número de telefone.'}, help_text='O País default para os números de telemóvel é Portugal(+351). Se o seu número for de um país diferente tem de adicionar o identificador desse país.', max_length=128, null=True, region=None, unique=True)),
                ('tipo_utilizador', models.CharField(choices=[('C', 'CONSUMIDOR'), ('F', 'FORNECEDOR')], default='', max_length=1, null=True)),
                ('imagem_perfil', models.ImageField(blank=True, default='imagens_perfil/avatar.png', null=True, upload_to='imagens_perfil/', validators=[loja.models.Utilizador.validar_extensao_imagens, loja.models.Utilizador.validar_tamanho_imagens])),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designa se este utilizador pode aceder à área de administração do site.')),
                ('is_admin', models.BooleanField(default=False, help_text='Designa se este utilizador tem permissão para realizar ações de administrador.')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Utilizador',
                'verbose_name_plural': 'Utilizadores',
                'ordering': ['id', 'username', 'telemovel', '-created', '-updated'],
            },
            managers=[
                ('objects', loja.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Atributo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Atributo',
                'verbose_name_plural': 'Atributos',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Carrinho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Carrinho',
                'verbose_name_plural': 'Carrinhos',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('categoria_pai', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categorias_filhas', to='loja.categoria')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Consumidor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utilizador', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='consumidor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Consumidor',
                'verbose_name_plural': 'Consumidores',
                'ordering': ['id', 'utilizador'],
            },
        ),
        migrations.CreateModel(
            name='DetalhesEnvio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('pais', django_countries.fields.CountryField(default='PT', max_length=2)),
                ('cidade', models.CharField(max_length=200)),
                ('telemovel', phonenumber_field.modelfields.PhoneNumberField(help_text='O País default para os números de telemóvel é Portugal(+351). Se o seu número for de um país diferente tem de adicionar o identificador desse país.', max_length=128, region=None)),
                ('email', models.EmailField(max_length=200)),
                ('morada', models.CharField(max_length=200)),
                ('instrucoes_entrega', models.TextField(blank=True, max_length=500, null=True)),
                ('usar_informacoes_utilizador', models.BooleanField(help_text='Usar informações guardadas ao criar conta?')),
                ('guardar_esta_morada', models.BooleanField(default=False, help_text='Deseja guardar esta morada para futuras encomendas?')),
                ('consumidor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='detalhes_envio', to='loja.consumidor')),
            ],
            options={
                'verbose_name': 'Detalhes de Envio',
                'verbose_name_plural': 'Detalhes de Envios',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Encomenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idCheckoutSession', models.CharField(max_length=200, null=True, verbose_name='idCheckoutSession')),
                ('valor_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('estado', models.CharField(choices=[('Em processamento', 'Em processamento'), ('Entregue', 'Entregue'), ('Cancelado', 'Cancelado')], default='Em processamento', max_length=20)),
                ('consumidor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encomendas', to='loja.consumidor')),
                ('detalhes_envio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='encomendas', to='loja.detalhesenvio')),
            ],
            options={
                'verbose_name': 'Encomenda',
                'verbose_name_plural': 'Encomendas',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utilizador', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fornecedor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Fornecedor',
                'verbose_name_plural': 'Fornecedores',
                'ordering': ['id', 'utilizador'],
            },
        ),
        migrations.CreateModel(
            name='Opcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('atributos', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.atributo')),
            ],
            options={
                'verbose_name': 'Opção disponivel',
                'verbose_name_plural': 'Opções disponiveis',
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('categoria', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='loja.categoria')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='ProdutosEncomenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.DecimalField(decimal_places=3, default=1, max_digits=6, null=True)),
                ('preco', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('precoKilo', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('estado', models.CharField(choices=[('Em processamento', 'Em processamento'), ('A sair da Unidade de Producao', 'A sair da Unidade de Producao'), ('Enviado', 'Enviado'), ('A chegar', 'A chegar'), ('Entregue', 'Entregue'), ('Cancelado', 'Cancelado')], default='Em processamento', max_length=30)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('encomenda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos', to='loja.encomenda')),
            ],
            options={
                'verbose_name': 'Produtos Encomendados',
                'verbose_name_plural': 'Produtos Encomendados',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='UnidadeProducao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, null=True)),
                ('pais', django_countries.fields.CountryField(default='PT', max_length=2, null=True)),
                ('cidade', models.CharField(max_length=100, null=True)),
                ('freguesia', models.CharField(max_length=100, null=True)),
                ('morada', models.CharField(max_length=200, null=True)),
                ('tipo_unidade', models.CharField(choices=[('A', 'Armazém'), ('Q', 'Quinta'), ('MM', 'Mini-mercado'), ('SM', 'Supermercado'), ('HM', 'Hipermercado'), ('LR', 'Loja de Rua'), ('LCC', 'Loja Centro Comercial'), ('O', 'Outro')], default='', max_length=5, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('fornecedor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unidades_producao', to='loja.fornecedor')),
            ],
            options={
                'verbose_name': 'Unidade de Producao',
                'verbose_name_plural': 'Unidades de Producao',
                'ordering': ['id', 'nome', 'fornecedor'],
            },
        ),
        migrations.CreateModel(
            name='Veiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, null=True)),
                ('tipo_veiculo', models.CharField(choices=[('C', 'Carro'), ('E', 'Estafeta a pé'), ('M', 'Mota'), ('B', 'Bicicleta'), ('T', 'Trotineta'), ('CR', 'Carrinha'), ('CM', 'Camião')], default='', max_length=5, null=True)),
                ('estado_veiculo', models.CharField(choices=[('D', 'Disponível'), ('C', 'A  ser carregado'), ('E', 'A entregar encomendas'), ('I/M', 'Indisponível/Manutenção'), ('R', 'Regresso')], default='D', max_length=5, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('unidadeProducao', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='veiculos', to='loja.unidadeproducao')),
            ],
            options={
                'verbose_name': 'Veiculo',
                'verbose_name_plural': 'Veiculos',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='ProdutoUnidadeProducao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0)])),
                ('descricao', models.TextField(blank=True, max_length=200, null=True)),
                ('unidade_medida', models.CharField(choices=[('kg', 'Quilograma'), ('g', 'Grama'), ('l', 'Litro'), ('ml', 'Mililitro'), ('un', 'Unidade')], help_text='Unidade de medida de venda e do stock. O seu produto vende-se à unidade/peso/volume?', max_length=2)),
                ('preco_a_granel', models.DecimalField(blank=True, decimal_places=2, help_text='Preço de venda a granel. Unidade monetária: Euro(€). Utilize um ponto, em vez de uma vírgula', max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('unidade_Medida_Por_Unidade', models.CharField(blank=True, choices=[('kg', 'Quilograma'), ('g', 'Grama'), ('l', 'Litro'), ('ml', 'Mililitro'), ('un', 'Unidade')], help_text='Caso o produto seja vendido à unidade, qual é a unidade de medida dessa unidade? Por exemplo, se for uma posta de carne/peixe, que unidade de medida tem essa posta (quanto pesa a posta). Ou se forem produtos que não precisam de dizer quanto tem de peso/volume, como um brinquedo/filme, selecione unidade', max_length=2, null=True)),
                ('quantidade_por_unidade', models.DecimalField(blank=True, decimal_places=2, help_text='Quanto tem o produto que vende à unidade? Quanto pesa a posta de carne/peixe? Ou se forem berlindes, quantos berlindes vende de uma vez?', max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('preco_por_unidade', models.DecimalField(blank=True, decimal_places=2, help_text='Preço unitário do produto que vende.', max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('data_producao', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('marca', models.CharField(blank=True, max_length=100, null=True)),
                ('imagem_produto', models.ImageField(help_text='Formatos aceites: PNG,JPG,SVG,GIF, Tamanho máximo:2MB', null=True, upload_to='products/', validators=[loja.models.ProdutoUnidadeProducao.validar_extensao_imagens, loja.models.ProdutoUnidadeProducao.validar_tamanho_imagens])),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_producao', to='loja.produto')),
                ('unidade_producao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos', to='loja.unidadeproducao')),
            ],
            options={
                'verbose_name': 'Produto por Unidade Producao',
                'verbose_name_plural': 'Produtos por Unidade Producao',
                'ordering': ['id', 'produto', 'unidade_producao'],
                'unique_together': {('produto', 'unidade_producao')},
            },
        ),
        migrations.CreateModel(
            name='ProdutosEncomendadosVeiculos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('produto_Encomendado', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='veiculo_transporte', to='loja.produtosencomenda')),
                ('veiculo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos_no_veiculo', to='loja.veiculo')),
            ],
            options={
                'verbose_name': 'Produto Associado a Veículo',
                'verbose_name_plural': 'Produtos Associados a Veículos',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='produtosencomenda',
            name='produtos',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Encomendado', to='loja.produtounidadeproducao'),
        ),
        migrations.AddField(
            model_name='produtosencomenda',
            name='unidadeProducao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Encomendas', to='loja.unidadeproducao'),
        ),
        migrations.CreateModel(
            name='ProdutosCarrinho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.DecimalField(decimal_places=3, default=1, max_digits=6, null=True)),
                ('preco', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('precoKilo', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('carrinho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos_carrinho', to='loja.carrinho')),
                ('produto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.produtounidadeproducao')),
            ],
            options={
                'verbose_name': 'Produtos num Carrinho',
                'verbose_name_plural': 'Produtos num Carrinho',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ProdutoOpcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opcao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loja.opcao')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opcoes', to='loja.produtounidadeproducao')),
            ],
            options={
                'verbose_name': 'Opção guardada',
                'verbose_name_plural': 'Opções guardadas',
            },
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('lido', models.BooleanField(default=False)),
                ('mensagem', models.CharField(blank=True, max_length=1000, null=True)),
                ('destinatario', models.CharField(choices=[('Consumidor', 'Consumidor'), ('Fornecedor', 'Fornecedor')], default='Fornecedor', max_length=20)),
                ('consumidor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.consumidor')),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loja.fornecedor')),
            ],
            options={
                'verbose_name': 'Notificacao',
                'verbose_name_plural': 'Notificacoes',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Imagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagem', models.ImageField(upload_to='produtos/imagens/')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagens_produto', to='loja.produtounidadeproducao')),
            ],
        ),
        migrations.CreateModel(
            name='CategoriaAtributo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atributo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loja.atributo')),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.categoria')),
            ],
            options={
                'verbose_name': 'Categoria Atributo',
                'verbose_name_plural': 'Categoria Atributos',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='carrinho',
            name='consumidor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='carrinho', to='loja.consumidor'),
        ),
    ]
