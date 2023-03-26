import phonenumbers
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class Utilizador(AbstractUser):
    CONSUMIDOR = 'C'
    FORNECEDOR = 'F'
    TIPO_UTILIZADOR = [
        (CONSUMIDOR, 'CONSUMIDOR'),
        (FORNECEDOR, 'FORNECEDOR')
    ]
    nome = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True, blank=False)
    pais = models.CharField(max_length=200, null=True, blank=False)
    cidade = models.CharField(max_length=200, null=True, blank=False) 
    morada = models.CharField(max_length=200, null=True, blank=False)
    telemovel = PhoneNumberField(null=True, blank=False, unique=True)
    tipo_utilizador = models.CharField(max_length=1, choices=TIPO_UTILIZADOR, default='', null=True, blank=False)
    imagem_perfil = models.ImageField(null=True, default="avatar.svg")
    
    updated = models.DateTimeField(auto_now=True, null=True, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pais','cidade','morada','telemovel','tipo_utilizador']
    
    
    
    class Meta:
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
    # lista_unidades_producao
    descricao = models.TextField(blank=True, null=True, max_length=500)
    def __str__(self):
        return self.utilizador.nome


class UnidadeProducao(models.Model):
    TIPO_UNIDADE = [
        ('A', 'Armazém'),
        ('Q', 'Quinta'),
        ('MM', 'Mini-mercado'),
        ('SM', 'Supermercado'),
        ('HM', 'Hipermercado'),
        ('LR', 'Loja de Rua'),
        ('LCC', 'Loja Centro Comercial'),
    ]
    fornecedor = models.ForeignKey(Fornecedor, null=True, blank=False, on_delete=models.CASCADE)
    pais = models.CharField(max_length=100, null=True, blank=False)
    cidade = models.CharField(max_length=100, null=True, blank=False)
    # freguesia = models.CharField(max_length=100, null=True, blank=False)
    morada = models.CharField(max_length=100, null=True, blank=False)
    tipo_unidade = models.CharField(max_length=1, choices=TIPO_UNIDADE, default='', null=True, blank=False)
    # lista produtos
    

class Tipo(models.Model):
    """
    Tipo de produto.
    

    Args:
        models (_type_): _description_
    ----------------------------------------------------------------
    nome: CharField. str 
        nome do tipo de produto. Por exemplo: Roupa
    pai: CharField. str
        esta classe é descendente de outra? Por exemplo: 
        Roupa --> Roupa Criança.  Roupa Criança é descendente
        de Roupa
    """

    nome = models.CharField(max_length=100, blank=False, null=True)
    pai = models.ForeignKey("Tipo", blank=True, null=True, on_delete=models.CASCADE)
    
    created = models.DateTimeField(auto_now_add=True, null=True, blank=False)   