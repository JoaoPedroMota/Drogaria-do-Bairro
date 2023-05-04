import phonenumbers
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.models import UserManager
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_countries.fields import CountryField
# Create your models here.


class CustomUserManager(UserManager):
    """
    Classe que define um gerenciador personalizado de usuários. Ela estende a classe UserManager
    do Django e adiciona comportamentos personalizados para a criação de usuários comuns e 
    superusuários.

    Atributos:
        Nenhum atributo adicional além dos herdados da classe UserManager.

    Métodos:
        create_user(email, password=None, **extra_fields): Cria e salva um usuário comum com
            o email e senha fornecidos e quaisquer campos extras especificados em extra_fields.
            Se a senha não for fornecida, uma senha aleatória será gerada. Se is_staff e 
            is_admin não estiverem definidos em extra_fields, eles serão definidos como False.
            Retorna o usuário criado.

        create_superuser(password=None, **extra_fields): Cria e salva um superusuário com a 
            senha fornecida e quaisquer campos extras especificados em extra_fields. Se a senha 
            não for fornecida, uma senha aleatória será gerada. Se is_staff, is_admin e 
            is_superuser não estiverem definidos em extra_fields, eles serão definidos como True.
            Retorna o superusuário criado.
    Comentário:
    POR FAVOR NÃO MEXER NESTA CLASSE. EVITAR AO MÁXIMO!!!!!!!!
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário comum com o email e senha fornecidos e quaisquer campos extras 
        especificados em extra_fields. Se a senha não for fornecida, uma senha aleatória será 
        gerada. Se is_staff e is_admin não estiverem definidos em extra_fields, eles serão 
        definidos como False.

        Args:
            email (str): O email do usuário a ser criado.
            password (str): A senha do usuário a ser criado. Se não for fornecida, uma senha 
                aleatória será gerada.
            **extra_fields: Campos extras para adicionar ao usuário.

        Returns:
            O usuário comum criado.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_admin', False)
        return super().create_user(email, password=password, **extra_fields)

    def create_superuser(self, password=None, **extra_fields):
        """
        Cria e salva um superusuário com a senha fornecida e quaisquer campos extras especificados 
        em extra_fields. Se a senha não for fornecida, uma senha aleatória será gerada. Se is_staff,
        is_admin e is_superuser não estiverem definidos em extra_fields, eles serão definidos como 
        True.

        Args:
            password (str): A senha do superusuário a ser criado. Se não for fornecida, uma senha 
                aleatória será gerada.
            **extra_fields: Campos extras para adicionar ao superusuário.

        Returns:
            O superusuário criado.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return super().create_superuser(password=password, **extra_fields)


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
    
    # Definindo as opções para o campo tipo_utilizador
    CONSUMIDOR = 'C'
    FORNECEDOR = 'F'
    TIPO_UTILIZADOR = [
        (CONSUMIDOR, 'CONSUMIDOR'),
        (FORNECEDOR, 'FORNECEDOR')
    ]

    # Campos personalizados
    nome = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True, blank=False, error_messages={'unique': 'Já existe um utilizador com esse e-mail.'})
    username = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=False,
        validators=[ASCIIUsernameValidator()],
        help_text='Máximo 20 caracteres. Apenas letras, números e os seguintes símbolos @/./+/-/_ ',
        error_messages={
            'unique': 'Já existe um utilizador com esse nome de utilizador.',
        },
    )
    pais = CountryField(null=True, blank=False, default='PT')
    cidade = models.CharField(max_length=200, null=True, blank=False) 
    #morada = models.CharField(max_length=200, null=True, blank=False)
    telemovel = PhoneNumberField(null=True, blank=True, unique=True, error_messages={'unique': 'Já existe um utilizador com esse número de telefone.'}, help_text='O País default para os números de telemóvel é Portugal(+351). Se o seu número for de um país diferente tem de adicionar o identificador desse país.')
    tipo_utilizador = models.CharField(max_length=1, choices=TIPO_UTILIZADOR, default='', null=True)
    imagem_perfil = models.ImageField(null=True, default="avatar.svg")
    
    # Campos padrão
    is_staff = models.BooleanField(default=False, help_text='Designa se este utilizador pode aceder à área de administração do site.')
    is_admin = models.BooleanField(default=False, help_text='Designa se este utilizador tem permissão para realizar ações de administrador.')
    
    # Campo personalizado de username

    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)
    
    # Definindo o campo de email como o identificador exclusivo do usuário
    USERNAME_FIELD = 'email'

    # Definindo que os campos personalizados são obrigatórios apenas no momento do registro de usuário
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()
    
    
    def is_fornecedor(self):
        return self.tipo_utilizador == Utilizador.FORNECEDOR
    
    def is_consumidor(self):
        return self.tipo_utilizador == Utilizador.CONSUMIDOR
    
    
    
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
    
    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'
        ordering = ['username', '-created', '-updated']
    
    
class Consumidor(models.Model):
    utilizador = models.OneToOneField(Utilizador, on_delete=models.CASCADE, null=False, related_name='consumidor')
    #carrinho = carrinho atual
    # encomendas = Models.OneToMany
    def __str__(self):
        return self.utilizador.nome
    class Meta:
        verbose_name = 'Consumidor'
        verbose_name_plural = 'Consumidores'
    
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
    unidadeProducao = models.ForeignKey("UnidadeProducao", null=True, blank=False, on_delete=models.CASCADE)
    tipo_veiculo = models.CharField(max_length=5, choices=TIPO_VEICULO, default='', null=True, blank=False)
    estado_veiculo = models.CharField(max_length=5, choices=ESTADO_VEICULO, default='D', null=True, blank=False)

    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)

    @property
    def estado(self):
        return self.estado_veiculo
    
    def __str__(self):
        return self.nome
    
    
    
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


class Fornecedor(models.Model):
    utilizador = models.OneToOneField(Utilizador, on_delete=models.CASCADE, null=False, related_name='fornecedor')
    #lista_produtos
    #lista_veiculos
    descricao = models.TextField(blank=True, null=True, max_length=500)
    def __str__(self):
        return self.utilizador.nome
    
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
        
class Produto(models.Model):

    UNIDADES_MEDIDA_CHOICES = (
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'litro'),
        ('un', 'Unidade'),
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    categoria = models.TextField()
    #categoria = models.ForeignKey("Categoria", on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    unidade_medida = models.CharField(max_length=2, choices=UNIDADES_MEDIDA_CHOICES)
    data_validade = models.DateField()
    data_producao = models.DateField()
    unidade_producao = models.ForeignKey(UnidadeProducao, on_delete=models.CASCADE)
    marca = models.TextField()
    #marca = models.ForeignKey("Marca", on_delete=models.CASCADE)    
    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    #descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField(max_length=100)
    #descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Marca(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
# loja/migrations/000X_auto_add_slug_to_produto.py



