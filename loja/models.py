import phonenumbers
from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.models import UserManager
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_countries.fields import CountryField
from phonenumbers import format_number, PhoneNumberFormat
from functools import partial
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django_countries.widgets import CountrySelectWidget




# from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.


class CustomUserManager(UserManager):
    """
    Classe que define um gestor personalizado de utilizadores. Estende a classe UserManager
    do Django e adiciona comportamentos personalizados para a criação de superusers.

    Atributos:
        Nenhum atributo adicional além dos herdados da classe UserManager.

    Métodos:
        create_superuser(password=None, **outros_campos): Cria e salva um superuser com a 
            password fornecida. Se a password não for fornecida, uma aleatória será criada. 
            Se is_staff, is_admin e is_superuser não estiverem definidos em outros_campos, eles serão definidos como True.
            Retorna o superuser criado.
    Comentário:
    POR FAVOR NÃO MEXER NESTA CLASSE. EVITAR AO MÁXIMO!!!!!!!!
    """
    def create_superuser(self, password=None, **outros_campos):
        """
        Cria e salva um utilizador super com direitos de admin e password fornecida.
        Se a password não for fornecida, uma aleatória será criada. Se is_staff,
        is_admin e is_superuser não estiverem definidos em outros_campos, eles serão definidos como 
        True.

        Args:
            password (str): A senha do superuser a ser criado. Se não for fornecida, uma aleatória será gerada.
            **outros_campos: Campos extras para adicionar ao superuser.
        Returns:
            O superuser criado.
        """
        outros_campos.setdefault('is_superuser', True)
        outros_campos.setdefault('is_staff', True)

        outros_campos.setdefault('is_admin', True)
        return super().create_superuser(password=password, **outros_campos)


class Utilizador(AbstractUser):
    """
    Utilizador é uma classe de utilizador personalizada que estende a classe AbstractUser padrão do Django.
    Ele adiciona campos personalizados para lidar com informações de perfil do usuário, como nome, telefone,
    país, cidade e morada. Ele também adiciona um campo username para permitir que os usuários definam
    um nome de usuário personalizado, mas o campo de email é usado como identificador exclusivo do usuário.
    FIXME:
        EVITAR AO MÁXIMO MEXER NESTE MODELO. NÃO APAGAR DE MANEIRA ALGUMA OS SEGUINTES CAMPOS_
            is_staff
            is_admin
            USERNAME_FIELD
            REQUIRED_FIELDS
            objects = CustomUserManager()
        MANTER SEMPRE ESTAS FUNÇÕES:
            has_perm
            has_module_perms
        
    
    """
    def validar_extensao_imagens(value):
        ext = value.name.split('.')[-1].lower()
        allowed_extensions = ['jpg','png','svg','gif']
        if ext not in allowed_extensions:
            raise ValidationError((f'Tipo de ficheiro inválido. Extensões válidas: {allowed_extensions}'))
    def validar_tamanho_imagens(value):
        max_size = 2 * 1024 * 1024
        if value.size > max_size:
            raise ValidationError((f'Ficheiro grande de mais. Tamanho máximo 2MB'))
    
    # Definindo as opções para o campo tipo_utilizador
    CONSUMIDOR = 'C'
    FORNECEDOR = 'F'
    TIPO_UTILIZADOR = [
        (CONSUMIDOR, 'CONSUMIDOR'),
        (FORNECEDOR, 'FORNECEDOR')
    ]
    
    # Campos personalizados
    nome = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=False, error_messages={'unique': 'Já existe um utilizador com esse e-mail.'})
    username = models.CharField(max_length=20, unique=True, null=True, blank=False, validators=[ASCIIUsernameValidator()], help_text='Máximo 20 caracteres. Apenas letras, números e os seguintes símbolos @/./+/-/_ ', error_messages={ 'unique': 'Já existe um utilizador com esse nome de utilizador.',},)
    pais = CountryField(null=True, blank=False, default='PT')
    cidade = models.CharField(max_length=200, blank=True, default='') 
    #morada = models.CharField(max_length=200, null=True, blank=False)
    telemovel = PhoneNumberField(null=True, blank=True, default='', unique=True, error_messages={'unique': 'Já existe um utilizador com esse número de telefone.'}, help_text='O País default para os números de telemóvel é Portugal(+351). Se o seu número for de um país diferente tem de adicionar o identificador desse país.')
    tipo_utilizador = models.CharField(max_length=1, choices=TIPO_UTILIZADOR, default='', null=True)
    imagem_perfil = models.ImageField(null=True, default="avatar.svg", validators=[validar_extensao_imagens, validar_tamanho_imagens])
    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)  
    
    # Campos padrão para admin
    is_staff = models.BooleanField(default=False, help_text='Designa se este utilizador pode aceder à área de administração do site.')
    is_admin = models.BooleanField(default=False, help_text='Designa se este utilizador tem permissão para realizar ações de administrador.')
    def has_perm(self, perm, obj=None):
        """
        Retorna True se o utilizador tem a permissão especificada. Este método é necessário para compatibilidade com o Django Admin.
        """
        return self.is_admin
    
    def has_module_perms(self, app_label):
        """
        Retorna True se o utilizador tem permissões para ver o aplicativo 'app_label'. Este método é necessário para compatibilidade com o Django Admin.
        """
        return self.is_admin and self.is_superuser
    # Campo personalizado de username


    
    # Definindo o campo de email como o identificador exclusivo do usuário
    USERNAME_FIELD = 'email'
    # Definindo que os campos personalizados são obrigatórios apenas no momento do registro de usuário
    REQUIRED_FIELDS = ['username']
    #gerir superusers
    objects = CustomUserManager()
    
    
    
    
    #legibilidade na bd e do objeto
    def __repr__(self):
        return f"Utilizador(nome='{self.nome}', email='{self.email}', username='{self.username}', pais='{self.pais}', cidade='{self.cidade}', telemovel='{self.telemovel}', tipo_utilizador='{self.tipo_utilizador}', imagem_perfil='{self.imagem_perfil}', is_staff={self.is_staff}, is_admin={self.is_admin}, updated='{self.updated}', created='{self.created}')"
    def __str__(self):
        return self.username
    # legibilidade humana para debug e cenas
    @property
    def representacao(self):
        numero_formatado = format_number(self.telemovel,PhoneNumberFormat.INTERNATIONAL )
        texto= f"\n\
                Nome:{self.nome}\n\
                Email:{self.email}\n\
                Username:{self.username}\n\
                País:{self.pais}\n\
                Cidade:{self.cidade}\n\
                Telemóvel:{numero_formatado}\n\
                "
        if self.tipo_utilizador == 'C':
            texto+= "Tipo Utilizador: Consumidor"
        else:
            texto+= "Tipo Utilizador: Fornecedor"
        return texto
    
    #funcionalidades
    @property
    def is_fornecedor(self):
        return self.tipo_utilizador == Utilizador.FORNECEDOR
    @property
    def is_consumidor(self):
        return self.tipo_utilizador == Utilizador.CONSUMIDOR

    @property
    def produtosCarrinho(self):
        if self.is_consumidor():
            carrinho = self.consumidor.carrinho
            produtosNoCarrinho = carrinho.produtos_carrinho.all()
            return produtosNoCarrinho
        else:
            raise ValueError("Apenas os utilizadores que são consumidores têm carrinho, e só estes podem aceder aos produtos que têm no carrinho.")


    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'
        ordering = ['id','username','telemovel' ,'-created', '-updated']
    
    
class Consumidor(models.Model):
    utilizador = models.OneToOneField(Utilizador, on_delete=models.CASCADE, null=False, related_name='consumidor')
    #carrinho = carrinho atual
    # encomendas = Models.OneToMany
    def __str__(self):
        return self.utilizador.username
    class Meta:
        verbose_name = 'Consumidor'
        verbose_name_plural = 'Consumidores'
        ordering=['id','utilizador']
    def save(self, *args, **kwargs):
        if Fornecedor.objects.filter(utilizador=self.utilizador).exists():
            raise ValueError('O utilizador já está associado a um Fornecedor.')
        super(Consumidor, self).save(*args, **kwargs)
    
class Veiculo(models.Model):
    carro = 'C'
    estafeta = 'E'
    mota = 'M'
    bicicleta = 'B'
    trotineta = 'T'
    carrinha = 'CR'
    camiao = 'CM'
    TIPO_VEICULO = [
        (carro, 'Carro'),
        (estafeta, 'Estafeta a pé'),
        (mota, 'Mota'),
        (bicicleta, 'Bicicleta'),
        (trotineta, 'Trotineta'),
        (carrinha, 'Carrinha'),
        (camiao, 'Camião'),
    ]
    disponivel = 'D'
    aCaminho = 'A-C'
    aEntregar = 'E'
    indisponivel = 'I/M'
    regresso = 'R'
    espera = 'W'
    ESTADO_VEICULO = [
        (disponivel, 'Disponível'),
        (aCaminho, 'A caminho'),
        (aEntregar, 'A entregar'),
        (indisponivel, 'Indisponível/Manutenção'),
        (regresso, 'Regresso'),
        (espera, 'À espera'),
        
    ]
    nome = models.CharField(max_length=200, null=True, blank=False)
    unidadeProducao = models.ForeignKey("UnidadeProducao", null=True, blank=False, on_delete=models.CASCADE, related_name='veiculos')
    tipo_veiculo = models.CharField(max_length=5, choices=TIPO_VEICULO, default='', null=True, blank=False)
    estado_veiculo = models.CharField(max_length=5, choices=ESTADO_VEICULO, default='D', null=True, blank=False)

    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)

    @property
    def estado(self):
        return self.estado_veiculo
    
    def __str__(self):
        try:
            return self.nome
        except AttributeError:
            return "Veículo sem nome"
    class Meta:
        verbose_name_plural = "Veículos"
        verbose_name = "Veículo"
        ordering= ['id','unidadeProducao','nome', 'tipo_veiculo','estado_veiculo','-created','-updated']

    def __repr__(self):
        return f"Veiculo(nome='{self.nome}', unidadeProducao='{self.unidadeProducao}', tipo_veiculo='{self.tipo_veiculo}', estado_veiculo='{self.estado_veiculo}')"

    class Meta:
        verbose_name = 'Veiculo'
        verbose_name_plural = 'Veiculos'
        ordering = ['nome']

    
    
class UnidadeProducao(models.Model):
    """_summary_
    Args:
        models (_type_): _description_
    ----------------------------------
    TIPO_UNIDADE : list
        tipo de unidades possiveis. Mais tarde poderá ser uma classe
    fornecedor: foreignkey
        referencia quem é o fornecedor dono desta unidade de producao
    pais: charfield. str
        em que país está esta unidade de producao
    cidade: charfield. str
        em que cidade está esta unidade de producao
    morada: charfield. str
        qual é a morada desta unidade de producao. (Rua Torta 4 3ºD)
        
    tipo_unidade: charfield. str
        que tipo de unidade é esta de facto
    """
    TIPO_UNIDADE = [
        ('A', 'Armazém'),
        ('Q', 'Quinta'),
        ('MM', 'Mini-mercado'),
        ('SM', 'Supermercado'),
        ('HM', 'Hipermercado'),
        ('LR', 'Loja de Rua'),
        ('LCC', 'Loja Centro Comercial'),
        ('O', 'Outro')
    ]
    nome = models.CharField(max_length=200, null=True, blank=False)
    fornecedor = models.ForeignKey("Fornecedor", null=True, blank=False, on_delete=models.CASCADE, related_name="unidades_producao")
    pais = CountryField(null=True, blank=False, default='PT')
    #pais = CountryField(null=True, blank=False, default='PT', widgets=CountrySelectWidget())
    cidade = models.CharField(max_length=100, null=True, blank=False)
    # freguesia = models.CharField(max_length=100, null=True, blank=False)
    morada = models.CharField(max_length=200, null=True, blank=False)
    tipo_unidade = models.CharField(max_length=5, choices=TIPO_UNIDADE, default='', null=True, blank=False)

    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)

    # lista produtos
    def get_all_veiculos(self):
        return Veiculo.objects.filter(unidadeProducao=self)
    
    def get_veiculo_por_id(self, id):
        try:
            veiculo = Veiculo.objects.get(id=id)
            if veiculo in self.get_veiculos():
                return veiculo
            else:
                raise ValueError('Esta veiculo não pertence a esta unidade de producao')
        except Veiculo.DoesNotExist:
            raise ValueError('Não encontrei nenhum veículo com base no id dado')
        
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name_plural = "Unidades de Producao"
        verbose_name = "Unidade de Producao"
        ordering=['id', 'nome','fornecedor']


class Fornecedor(models.Model):
    utilizador = models.OneToOneField(Utilizador, on_delete=models.CASCADE, null=False, related_name='fornecedor')
    #lista_produtos
    #lista_veiculos
    #descricao = models.TextField(blank=True, null=True, max_length=500)   
    def __str__(self):
        return self.utilizador.username
    
    def get_all_unidadesProducao(self):
        return UnidadeProducao.objects.filter(fornecedor=self)
    
    def get_unidade_producao_por_id(self, id):
        try:
            unidade = UnidadeProducao.objects.get(id=id)
            if unidade in self.get_unidades_producao():
                return unidade
            else:
                raise ValueError('Esta unidade de produção não pertence a este fornecedor')
        except UnidadeProducao.DoesNotExist:
            raise ValueError('Não encontrei nenhuma unidade de produção com base no id dado')
    def save(self, *args, **kwargs):
        if Consumidor.objects.filter(utilizador=self.utilizador).exists():
            raise ValueError('O utilizador já está associado como um Consumidor.')
        super(Fornecedor, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = "Fornecedores"
        verbose_name = "Fornecedor"
        ordering=['id', 'utilizador']
        



##############################################PRODUTOS#######################################################





def generate_slug(name):
    slug = slugify(name)
    counter = 0
    while Produto.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{slug}-{counter}"
    return slug


#from .views import adicionar_atributos_a_subcategorias

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True) 
    #slug = models.SlugField(max_length=50, unique=True)                               #default=1,
    categoria_pai = models.ForeignKey('Categoria', on_delete=models.SET_NULL,  null=True, blank=True, related_name="categorias_filhas")
    def __str__(self):
        return self.nome
    
    
    def __repr__(self):
        if self.categoria_pai is None:
            return f'Categoria.objects.create(nome="{self.nome}", categoria_pai = None)'
        else:
            return f'Categoria.objects.create(nome="{self.nome}", categoria_pai={self.categoria_pai.id})'
    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"
        ordering = [ 'id'   ,'nome']

    def save(self, *args, **kwargs):
        # Chame o método save da classe pai para salvar a categoria
        super().save(*args, **kwargs)

class Produto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=False, null=True, default=1)
    class Meta:
        verbose_name_plural = "Produtos"
        verbose_name = "Produto"
    def __str__(self):
        return self.nome
    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = generate_slug(self.nome)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ("id","nome")

class ProdutoUnidadeProducao(models.Model):
    UNIDADES_MEDIDA_CHOICES = (
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('un', 'Unidade'),
    )
    UNIDADES_MEDIDA_CHOICES_unidade = (
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('un', 'Unidade')
    )
    
    ### produto e unidade de produção
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='unidades_producao', blank=False, null=False)
    unidade_producao = models.ForeignKey(UnidadeProducao, on_delete=models.CASCADE, related_name='produtos')
    stock = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, validators=[MinValueValidator(0)])
    descricao = models.TextField(max_length=200, null=True, blank=True)    
    #cenas a granel
    unidade_medida = models.CharField(max_length=2, choices=UNIDADES_MEDIDA_CHOICES, null=False, blank=False)
    preco_a_granel = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    ###cenas à unidade
    unidade_Medida_Por_Unidade = models.CharField(max_length=2,choices=UNIDADES_MEDIDA_CHOICES_unidade, null=True, blank=True)
    quantidade_por_unidade = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    preco_por_unidade = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])  
    # outras cenas
    data_producao = models.DateField( null=True,blank=True, default=timezone.now)
    marca = models.CharField(max_length=100, null=True, blank=True)

    def get_imagem(self):
        from .imagem import Imagem
        return Imagem.objects.get(produto=self)
    def __str__(self):
        return f'Produto: {self.produto.nome} da Unidade de Produção: {self.unidade_producao.nome}'

    class Meta:
        verbose_name_plural = "Produtos por Unidade Producao"
        verbose_name = "Produto por Unidade Producao"
        ordering=['id','produto','unidade_producao']
        unique_together = ('produto', 'unidade_producao')

    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError(f"Já existe este produto ({self.produto}) nesta unidade de produção ({self.unidade_producao}). Não pode ter o mesmo produto na mesma unidade de produção. Altere um dos campos.")
    
    def clean(self):
        super().clean()
        if self.unidade_medida == 'un':
            if self.preco_a_granel is not None:
                raise ValidationError('O preço a granel não é permitido para produtos vendidos à unidade. Remova a este campo.')
            if self.unidade_Medida_Por_Unidade is None:
                raise ValidationError('Tem de introduzir a unidade de media da embalagem/unidade. Preencha o campo  "unidade_Medida_Por_Unidade"')
            
            if self.quantidade_por_unidade is None:
                raise ValidationError('A quantidade por unidade é obrigatória para produtos vendidos à unidade. Preencha o campo "quantidade_por_unidade"')
            
            if self.preco_por_unidade is None:
                raise ValidationError('O preço por unidade é obrigatório para produtos vendidos à unidade.')
            
        elif self.unidade_medida in ('kg', 'g', 'l', 'ml'):
            if self.unidade_Medida_Por_Unidade is not None:#A unidade de medida por unidade não é permitido para produtos vendidos por peso ou volume.
                raise ValidationError(f'Selecionou antes {dict(self.UNIDADES_MEDIDA_CHOICES).get(self.unidade_medida)} como unidade de medida deste produto. Este campo serve para indicar qual a unidade de medida do produto à venda. Remova a seleção do campo unidade de medida por unidade.')
            if self.quantidade_por_unidade is not None:
                raise ValidationError('A quantidade por unidade não é permitida para produtos vendidos por peso ou volume. Remova este campo.')
            if self.preco_por_unidade is not None:
                raise ValidationError('O preço por unidade não é permitido para produtos vendidos por peso ou volume. Remova este campo.')
            if self.preco_a_granel is None:
                raise ValidationError('O preço a granel é obrigatório para produtos vendidos por peso ou volume. Preencha o campo: Preço a granel.') 
        else:
            if self.unidade_medida == 'un':
                if self.unidade_Medida_Por_Unidade is None:
                    raise ValidationError('A unidade de medida para produtos vendidos à unidade é obrigatória. Preencha o campo: Unidade Medida Por Unidade')
                if self.quantidade_por_unidade is None:
                    raise ValidationError('A quantidade para produtos vendidos à unidade é obrigatória. Preencha o campo: Quantidade por unidade')
                if self.preco_por_unidade is None:
                    raise ValidationError('O preço por produtos vendidos à unidade é obrigatório. Preencha o campo: Preço por unidade')
            elif self.unidade_medida in ['kg', 'g', 'l', 'ml']:
                if self.preco_a_granel is None:
                   raise ValidationError('O preço a granel é obrigatório para produtos vendidos por peso ou volume. Preencha o campo: Preço a granel.') 
    
                
                
# class Imagem(models.Model):
#     produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens_produto')
#     foto = models.ImageField(upload_to='produtos_imagens/')

#     imagem = models.ImageField(upload_to='produtos/imagens/')

#     def __str__(self):
#         return f"Imagem do produto {self.produto.nome}"


#atributos vao ser diferentes para cada categoria
class Atributo(models.Model):
    nome = models.CharField(max_length=100)
    #por exemplo data-de-validade em vez de Data de Validade
    #slug = models.SlugField(null=True)
    #categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=1, null=True, blank=True)
    #true caso tenha opçoes especificas por exemplo tamanho(XS,S,M,L,XL), false caso contrario, peso por exemplo
    #is_variante = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Atributos"
        verbose_name = "Atributo"
        ordering=['id']
    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = generate_slug(self.nome)
        super().save(*args, **kwargs)       

from django.core.exceptions import ValidationError
from django.db import models
    
#ligaçao entre a tabela categoria e os atributos
class CategoriaAtributo(models.Model):
    # produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE)
    #valor = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categoria Atributos"
        verbose_name = "Categoria Atributo"
        ordering= ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            adicionar_atributos_a_subcategorias(self.categoria, self.atributo)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categoria.nome} - {self.atributo.nome}"


def adicionar_atributos_a_subcategorias(categoria, atributo):
    subcategorias = Categoria.objects.filter(categoria_pai=categoria)
    for subcategoria in subcategorias:
        # Verifique se já existe uma instância de CategoriaAtributo para a combinação de categoria e atributo
        if not CategoriaAtributo.objects.filter(categoria=subcategoria, atributo=atributo).exists():
            categoria_atributo = CategoriaAtributo(categoria=subcategoria, atributo=atributo)
            categoria_atributo.save()
        adicionar_atributos_a_subcategorias(subcategoria, atributo)


#opçoes para os atributos, por exemplo cor: vermelho,verde,amarelo
class Opcao(models.Model):
    nome = models.CharField(max_length=100)
    atributos = models.ForeignKey(Atributo, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Opção disponivel"
        verbose_name_plural ="Opções disponiveis"
    def __str__(self):
        return f"{self.nome} - {self.atributos.nome}"


#para guardar as escolhas das opçoes para cada produto criado
class ProdutoOpcao(models.Model):
    produto = models.ForeignKey('ProdutoUnidadeProducao', on_delete=models.CASCADE, related_name='opcoes')
    opcao = models.ForeignKey('Opcao', on_delete=models.CASCADE)
    #valor = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.produto.nome} - {self.opcao.nome}: {self.valor}'

    class Meta:
        verbose_name = "Opção guardada"
        verbose_name_plural ="Opções guardadas"

class Carrinho(models.Model):
    consumidor = models.OneToOneField(Consumidor, null=False, on_delete=models.CASCADE, related_name='carrinho')
    
    def __str__(self):
        return f'Carrinho de {self.consumidor}'
    class Meta:
        verbose_name = "Carrinho"
        verbose_name_plural ="Carrinhos"
        ordering=['id']

class ProdutosCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='produtos_carrinho')
    produto = models.ForeignKey(ProdutoUnidadeProducao, on_delete=models.SET_NULL, null=True, blank = True)
    quantidade = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank = False, default= 1)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precoKilo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.carrinho}. {self.produto}'
    class Meta:
        verbose_name = "Produtos num Carrinho"
        verbose_name_plural = "Produtos num Carrinho"
        ordering = ['id']
    def save(self, *args, **kwargs):
        produto = ProdutoUnidadeProducao.objects.get(id=self.produto.id)
        if produto.unidade_medida in ['g', 'kg', 'ml', 'l']:
            self.precoKilo = produto.preco_a_granel
            self.preco = self.quantidade * self.precoKilo
        elif produto.unidade_medida == 'un':
            self.precoKilo = produto.preco_por_unidade
            self.preco = self.quantidade * self.precoKilo
        super(ProdutosCarrinho, self).save(*args, **kwargs)




class Encomenda(models.Model):
    consumidor = models.ForeignKey(Consumidor, on_delete=models.CASCADE, null=False, related_name="encomendas")
    class Meta:
        verbose_name = "Encomenda"
        verbose_name_plural = "Encomendas"
        ordering=['id']


class ProdutosEncomenda(models.Model):
    encomenda = models.ForeignKey(Encomenda, on_delete=models.CASCADE, null=False, related_name="produtos")
    produtos = models.ForeignKey(ProdutoUnidadeProducao, on_delete=models.CASCADE, null=False, related_name='Encomendado')
    class Meta:
        verbose_name = "Produtos Encomendados"
        verbose_name_plural = "Produtos Encomendados"
        ordering = ['id']