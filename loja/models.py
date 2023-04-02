import phonenumbers
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.models import UserManager
from django.core.exceptions import ValidationError
from django.db.models import Q
# Create your models here.


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_admin', False)
        return super().create_user(password=password, **extra_fields)

    def create_superuser(self, password=None, **extra_fields):
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
    """

    CONSUMIDOR = 'C'
    FORNECEDOR = 'F'
    TIPO_UTILIZADOR = [
        (CONSUMIDOR, 'CONSUMIDOR'),
        (FORNECEDOR, 'FORNECEDOR')
    ]

    # Campos personalizados
    nome = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True, blank=False, error_messages={'unique': 'Já existe um utilizador com esse e-mail.'})
    pais = models.CharField(max_length=200, null=True, blank=False)
    cidade = models.CharField(max_length=200, null=True, blank=False) 
    morada = models.CharField(max_length=200, null=True, blank=False)
    telemovel = PhoneNumberField(null=True, blank=True, unique=True, error_messages={'unique': 'Já existe um utilizador com esse número de telefone.'})
    tipo_utilizador = models.CharField(max_length=1, choices=TIPO_UTILIZADOR, default='', null=True)
    imagem_perfil = models.ImageField(null=True, default="avatar.svg")
    
    # Campos padrão
    is_staff = models.BooleanField(default=False, help_text='Designa se este utilizador pode aceder à área de administração do site.')
    is_admin = models.BooleanField(default=False, help_text='Designa se este utilizador tem permissão para realizar ações de administrador.')
    
    # Campo personalizado de username
    username = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=False,
        validators=[ASCIIUsernameValidator()],
        help_text='Obrigatório. 20 caracteres ou menos. Apenas letras, dígitos e @/./+/-/_ são permitidos.',
        error_messages={
            'unique': 'Já existe um utilizador com esse nome de utilizador.',
        },
    )
    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)
    # Definindo o campo de email como o identificador exclusivo do usuário
    USERNAME_FIELD = 'email'

    # Definindo que os campos personalizados são obrigatórios apenas no momento do registro de usuário
    REQUIRED_FIELDS = ['username']

    
    objects = CustomUserManager()
    def has_perm(self, perm, obj=None):
        """
        Retorna True se o utilizador tem a permissão especificada. Este método é necessário para compatibilidade com o Django Admin.
        """
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin and self.is_superuser
    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'
        ordering = ['username', '-created', '-updated']
    
    

    
class Consumidor(models.Model):
    utilizador = models.ForeignKey(Utilizador, on_delete=models.CASCADE, null=False, related_name='consumidor')
    #carrinho = carrinho atual
    # encomendas = Models.OneToMany
    def __str__(self):
        return self.utilizador.nome


class Fornecedor(models.Model):
    utilizador = models.ForeignKey(Utilizador, on_delete=models.CASCADE, null=False, related_name='fornecedor')
    #lista_produtos
    #lista_veiculos
    descricao = models.TextField(blank=True, null=True, max_length=500)
    def __str__(self):
        return self.utilizador.nome
    