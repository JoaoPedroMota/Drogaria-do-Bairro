import logging
from rest_framework.serializers import ModelSerializer, Field, SerializerMethodField, ValidationError
from rest_framework.fields import ImageField
#### MODELOS ####
from loja.models import Utilizador, Consumidor, UnidadeProducao, Fornecedor, Veiculo, Produto, Categoria, Carrinho, ProdutosCarrinho, ProdutoUnidadeProducao
from .utilidades_api import categorias_nao_pai
#######
from django_countries.fields import CountryField
from django_countries.serializers import CountryFieldMixin
from django_countries import countries
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password as django_validate_password
from rest_framework.serializers import CharField
from rest_framework import serializers
class TipoUtilizadorField(Field):
    def to_representation(self, value):
        return dict(Utilizador.TIPO_UTILIZADOR).get(value)

    def to_internal_value(self, data):
        for key, value in dict(Utilizador.TIPO_UTILIZADOR).items(): #separa as chaves dos valores do dicionário que está a ser criado ({'C':'CONSUMIDOR', 'F':'FORNECEDOR'})
            if key == data or value==data: #se a informação passada estiver na chave ou no valor, retorna a chave correspondente a esse valor ou chave
                return key
        raise ValidationError("Invalid tipo_utilizador description.")

class campoPaisSerializador(Field):
    """
    Para ser possivel serializar o campo País na classe utilizador
    """
    def to_representation(self, value):
        if value is not None:
            #return value.code
            return countries.name(value.code)

        return None


    def to_internal_value(self, data):
        if data is not None:
            try:
                #trys to find by the code
                country = CountryField().to_python(data)
                if country not in countries:
                    # Try to find the country by name
                    for country_code, country_name in countries:
                        if data.lower() == country_name.lower():
                            return CountryField().to_python(country_code)
                    raise ValidationError("Código de país inválido. Use este link para ver os códigos válidos: https://en.wikipedia.org/wiki/Regional_indicator_symbol")
                return country
            except:
                raise ValidationError("Código de país inválido. Use este link para ver os códigos válidos: https://en.wikipedia.org/wiki/Regional_indicator_symbol")
        return None



class TipoUnidadeProducaoField(Field):
    def to_representation(self, value):
        return dict(UnidadeProducao.TIPO_UNIDADE).get(value)

    def to_internal_value(self, data):
        for key, value in dict(UnidadeProducao.TIPO_UNIDADE).items(): #separa as chaves dos valores do dicionário que está a ser criado ({'C':'CONSUMIDOR', 'F':'FORNECEDOR'})
            if key == data or value==data: #se a informação passada estiver na chave ou no valor, retorna a chave correspondente a esse valor ou chave
                return key
        raise ValidationError(f"tipo_unidade inválida.Valor inserido não corresponde a nenhuma chave ou descrição.Valores possíveis:{dict(UnidadeProducao.TIPO_UNIDADE)}")



class TipoVeiculoField(Field):
    def to_representation(self, value):
        return dict(Veiculo.TIPO_VEICULO).get(value)

    def to_internal_value(self, data):
        for key, value in dict(Veiculo.TIPO_VEICULO).items(): #separa as chaves dos valores do dicionário que está a ser criado ({'C':'CONSUMIDOR', 'F':'FORNECEDOR'})
            if key == data or value==data: #se a informação passada estiver na chave ou no valor, retorna a chave correspondente a esse valor ou chave
                return key
        raise ValidationError(f"tipo_veiculo inválido.Valor inserido não corresponde a nenhuma chave ou descrição.Valores possíveis:{dict(Veiculo.TIPO_VEICULO)}")

class EstadoVeiculoField(Field):
    def to_representation(self, value):
        return dict(Veiculo.ESTADO_VEICULO).get(value)
    def to_internal_value(self, data):
        for key, value in dict(Veiculo.ESTADO_VEICULO).items():
            if key==data or value==data:
                return key
        raise ValidationError(f"estado_veiculo inválido. Valor inserido não corresponde a nenhuma chave ou descrição. Valores possíveis:{dict(Veiculo.ESTADO_VEICULO)}")




class UtilizadorSerializer(CountryFieldMixin, ModelSerializer):
    pais = campoPaisSerializador()
    tipo_utilizador = TipoUtilizadorField()
    password = CharField(write_only=True, required=False)
    nome = CharField(read_only=True)
    imagem_perfil = ImageField(required=False)
    def create(self, validated_data):
        if 'password' not in validated_data:
            raise ValidationError("password is required")
        if 'tipo_utilizador' not in validated_data:
            raise ValidationError("tipo_utilizador is required")
        if "email" not in validated_data:
            raise ValidationError("email is required")
        if "username" not in validated_data:
            raise ValidationError("username is required")
        if "pais" not in validated_data:
            raise ValidationError("pais is required")
        if 'cidade' not in validated_data:
            raise ValidationError("cidade is required")
        if "telemovel" not in validated_data:
            raise ValidationError("telemovel is required")
        validated_data['nome'] = f"{validated_data['first_name']} {validated_data['last_name']}"
        validated_data['cidade'] = validated_data['cidade'].upper()
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    def update(self, instance, validated_data):
        if 'tipo_utilizador' in validated_data and validated_data['tipo_utilizador'] != instance.tipo_utilizador:
            raise ValidationError(" 'tipo_utilizador' : 'Não se pode alterar o campo tipo_utilizador' ")
        if 'password' in validated_data:
            raise ValidationError(" Ainda não é possível editar o campo de palavra passe ")
        instance.username = validated_data.get('username', instance.username).lower()
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.nome = f"{instance.first_name} {instance.last_name}"
        instance.email = validated_data.get('email', instance.email)
        instance.pais = validated_data.get('pais', instance.pais)
        instance.cidade = validated_data.get('cidade', instance.cidade).upper()
        instance.telemovel = validated_data.get('telemovel', instance.telemovel)

        instance.save()
        return instance
    
    
    def validate_password(self, value):
        django_validate_password(value)  # Add this line to validate the password
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('password', None)
        return rep

    class Meta:
        model = Utilizador
        # fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'pais', 'cidade', 'nome', 'telemovel', 'tipo_utilizador']
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'pais', 'cidade', 'nome', 'telemovel', 'tipo_utilizador', 'imagem_perfil']
        extra_kwargs = {'password': {'required': True}}
    

class ConsumidorSerializer(ModelSerializer):
    utilizador = CharField(source="utilizador.username", read_only=True)
    class Meta:
        model = Consumidor
        fields = '__all__'
        
        
        
class FornecedorSerializer(ModelSerializer):
    utilizador = CharField(source="utilizador.username", read_only=True)
    class Meta:
        model = Fornecedor
        fields = ['id','utilizador']
        






class VeiculoSerializer(ModelSerializer):
    tipo_veiculo = TipoVeiculoField()
    estado_veiculo= EstadoVeiculoField()
    class Meta:
        model = Veiculo
        fields = ['id','nome', 'unidadeProducao', 'tipo_veiculo', 'estado_veiculo']
    def create(self, validated_data):
        if 'nome' not in validated_data:
            raise ValidationError("Nome is required")
        if 'unidadeProducao' not in validated_data:
            raise ValidationError("Unidade Producao is required")
        if 'tipo_veiculo' not in validated_data:
            raise ValidationError("Tipo Veiculo is required")
        if 'estado_veiculo' in validated_data and ('estado_veiculo'!='D' or 'estado_veiculo'!='Disponível'):
            raise ValidationError("Ao introduzir um novo veiculo a uma UP, este deve ser sempre introduzido como Disponivel (D)")
        return super().create(validated_data)
    
    
    

class UnidadeProducaoSerializer(ModelSerializer):
    pais = campoPaisSerializador()
    tipo_unidade = TipoUnidadeProducaoField()
    #veiculos = VeiculoSerializer(many=True, read_only=True)
    fornecedor = FornecedorSerializer(read_only=True)
    class Meta:
        model = UnidadeProducao
        fields = ['id','nome', 'pais', 'cidade', 'morada', 'tipo_unidade','fornecedor',]
    def save(self, **kwargs):
        self.validated_data['cidade'] = self.validated_data.get('cidade').upper()
        return super(UnidadeProducaoSerializer, self).save(**kwargs)

    ####def update(self, validated_data):
    

class CategoriaPaiSerializer(ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']

class CategoriaSerializer(ModelSerializer):
    categoria_pai = CategoriaPaiSerializer(read_only=True)
    class Meta:
        model = Categoria
        fields = ['id','nome', 'categoria_pai']

class CategoriaProduto(ModelSerializer):
    class Meta:
        model = Categoria
        fields= ['nome','id']




class ProdutoSerializer(ModelSerializer):
    categoria = CategoriaProduto()
    class Meta:
        model = Produto
        fields = ['id','nome', 'categoria']



class ProdutoSerializerRequest(serializers.ModelSerializer):
    categoria= serializers.CharField(write_only=True)  # Adicione este campo

    class Meta:
        model = Produto
        fields = ['id', 'nome', 'categoria']

    def validate_categoria_nome(self, value):
        categorias_validas = categorias_nao_pai()
        if value not in [categoria.nome for categoria in categorias_validas]:
            raise serializers.ValidationError("A categoria selecionada é inválida. Por favor, escolha uma categoria que não seja uma categoria pai.")
        return value

    def create(self, validated_data):
        if type(validated_data['categoria']) == str:
            categoria = validated_data.pop('categoria')
        elif type(validated_data['categoira']) == dict:
            categoria_temp = validated_data.pop('categoria')
            categoria = categoria_temp['nome']
        else:
            raise serializers.ValidationError("A categoria nem é uma string nem um dicionário válido.")
        try:
            categoria = Categoria.objects.get(nome=categoria)
        except Categoria.DoesNotExist:
            raise serializers.ValidationError(f"A categoria {categoria} não existe")
        produto = Produto.objects.create(categoria=categoria, **validated_data)
        return produto




class CarrinhoSerializer(ModelSerializer):
    consumidor = ConsumidorSerializer()
    class Meta:
        model = Carrinho
        fields = ['id', 'consumidor']


logger = logging.getLogger(__name__)

class ProdutoUnidadeProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ["id", "produto", "unidade_producao", "stock", "descricao", "unidade_medida", "preco_a_granel", "unidade_Medida_Por_Unidade", "quantidade_por_unidade", "preco_por_unidade", "data_producao", "marca"]
        read_only_fields = ['id']

    def verificar_existencia_associacao(self, produto, unidade_producao):
        existe_associacao = False

        if produto and unidade_producao:
            # Faça a verificação aqui e atribua o resultado à variável existe_associacao
            instance = self.instance
            queryset = ProdutoUnidadeProducao.objects.filter(produto=produto, unidade_producao=unidade_producao)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            existe_associacao = queryset.exists()

        return existe_associacao
    
    
    
    def validate(self, data):
        
        """
        A mesma coisa que o clean() no modelo ProdutoUnidadeProducao, mas para o serializador
        """
        
        
        
        unidade_medida = data.get('unidade_medida')
        preco_a_granel = data.get('preco_a_granel')
        unidade_Medida_Por_Unidade = data.get('unidade_Medida_Por_Unidade')
        quantidade_por_unidade = data.get('quantidade_por_unidade')
        preco_por_unidade = data.get('preco_por_unidade')
        produto = data.get('produto')
        unidade_producao = data.get('unidade_producao')
        
        
        if unidade_medida == 'un':
            if preco_a_granel is not None:
                raise serializers.ValidationError('O preço a granel não é permitido para produtos vendidos à unidade. Remova o campo preco_a_granel.')
            if unidade_Medida_Por_Unidade is None:
                raise serializers.ValidationError('Tem de introduzir a unidade de media da embalagem/unidade. Preencha o campo  \"unidade_Medida_Por_Unidade\"')
            
            if quantidade_por_unidade is None:
                raise serializers.ValidationError('A quantidade por unidade é obrigatória para produtos vendidos à unidade. Preencha o campo quantidade_por_unidade ')
            
            if preco_por_unidade is None:
                raise serializers.ValidationError('O preço por unidade é obrigatório para produtos vendidos à unidade.')
            
        elif unidade_medida in ('kg', 'g', 'l', 'ml'):
            if unidade_Medida_Por_Unidade is not None:
                raise serializers.ValidationError(f'Selecionou antes {unidade_medida} como unidade de medida deste produto. Este campo serve para indicar qual a unidade de medida do produto à venda. Remova o campo unidade_Medida_Por_Unidade.')
            if quantidade_por_unidade is not None:
                raise serializers.ValidationError('A quantidade por unidade não é permitida para produtos vendidos por peso ou volume. Remova este campo.')
            if preco_por_unidade is not None:
                raise serializers.ValidationError('O preço por unidade não é permitido para produtos vendidos por peso ou volume. Remova este campo.')
            if preco_a_granel is None:
                   raise serializers.ValidationError('O preço a granel é obrigatório para produtos vendidos por peso ou volume. Preencha o campo: Preço a granel.') 

        else:
            if unidade_medida == 'un':
                if unidade_Medida_Por_Unidade is None:
                    raise serializers.ValidationError('A unidade de medida para produtos vendidos à unidade é obrigatória. Preencha o campo: Unidade Medida Por Unidade')
                if quantidade_por_unidade is None:
                    raise serializers.ValidationError('A quantidade para produtos vendidos à unidade é obrigatória. Preencha o campo: Quantidade por unidade')
                if preco_por_unidade is None:
                    raise serializers.ValidationError('O preço por produtos vendidos à unidade é obrigatório. Preencha o campo: Preço por unidade')
            elif unidade_medida in ['kg', 'g', 'l', 'ml']:
                if preco_a_granel is None:
                   raise serializers.ValidationError('O preço a granel é obrigatório para produtos vendidos por peso ou volume. Preencha o campo: Preço a granel.') 
        if self.verificar_existencia_associacao(produto, unidade_producao):
            raise serializers.ValidationError("Já existe este produto ({produto}) nesta unidade de produção ({unidade_producao}). Não pode ter o mesmo produto na mesma unidade de produção. Altere um dos campos.")
        return data

    


 
        
class ProdutosCarrinhoResponseSerializer(ModelSerializer):
    """"
    Usado para responder a pedidos à API
    """
    produto = ProdutoUnidadeProducaoSerializer()
    carrinho = CarrinhoSerializer(read_only=True)
    class Meta:
        model= ProdutosCarrinho
        fields= ["carrinho", "produto", "quantidade","precoKilo","preco","id"]
        read_only = ["preco","precoKilo",'id', 'carrinho']


class TemProdutoNoCarrinhoSerializer(ModelSerializer):
    """"
    Usado para responder a pedidos à API
    """
    produto = ProdutoUnidadeProducaoSerializer()
    class Meta:
        model= ProdutosCarrinho
        fields= ["carrinho", "produto", "quantidade","precoKilo","preco","id"]
        read_only = ["preco","precoKilo",'id', 'carrinho']




        
class ProdutosCarrinhoRequestSerializer(ModelSerializer):
    """Usado para fazer pedidos À API e esta saber interpreta-los

    Args:
        ModelSerializer (_type_): _description_


    Returns:
        ProdutoCarrinhoSerializer: Um ProdutoCarrinho Serializado
    """
    produto = serializers.PrimaryKeyRelatedField(queryset=ProdutoUnidadeProducao.objects.all())
    carrinho = CarrinhoSerializer(read_only=True)
    class Meta:
        model= ProdutosCarrinho
        fields= ["carrinho", "produto", "quantidade","precoKilo","preco","id"]
        read_only = ["preco","precoKilo",'id', 'carrinho']
    def validate(self, data):
        quantidade = data.get('quantidade')
        produtoUP = data.get('produto')
        if quantidade < 0:
            raise serializers.ValidationError('A quantidade de um produto num carrinho tem de ser superior a 0')
        if produtoUP.unidade_medida=='un':
            parte_inteira = int(quantidade)
            parte_fracao = quantidade - parte_inteira
            if parte_fracao != 0:
                raise serializers.ValidationError(f'Produtos vendidos à unidade não podem ter quantidade não inteiras. Escolha um número sem parte fracionária')
        return data
    # def __init__(self, *args, **kwargs):
    #     super(ProdutosCarrinhoRequestSerializer, self).__init__(*args, **kwargs)
    #     instance = getattr(self, 'instance', None)
    #     if instance and instance.pk:
    #         self.fields['produto'].disabled = True



class FornecedorNomeUtilizadorSerializer(ModelSerializer):
    """Serializador de apoio  a UnidadeProducaoSingleProdutoSerializer
    Ver mais abaixo no codigo.
    Retirna o nome de um fornecedor. esse nome vem do utilizador associado ao proprio fornecedor

    Args:
        ModelSerializer (_type_): _description_
    """
    utilizador = CharField(source="utilizador.nome", read_only=True)
    class Meta:
        model = Fornecedor
        fields = ['utilizador','id']



class UnidadeProducaoSingleProdutoSerializer(ModelSerializer):
    """
    Serializador de auxilio a Single Product Serializer. Devolve o id, o fornecedor, isto é o nome do fornecedor da UP, a morada, cidade e pais da UP
    """
    fornecedor = FornecedorNomeUtilizadorSerializer(read_only=True)
    class Meta:
        model = UnidadeProducao
        fields = ['id','fornecedor', 'nome', 'morada', 'cidade', 'pais']
        read_only_fields = ['fornecedor']


class SingleProdutoPaginaSerializer(ModelSerializer):
    """Devolve um só produto da tabela ProdutoUnidadeProducao
    """
    unidade_producao = UnidadeProducaoSingleProdutoSerializer(read_only=True)
    produto = ProdutoSerializer()
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ["id","produto", "unidade_producao", "stock","descricao", "unidade_medida", "preco_a_granel", "unidade_Medida_Por_Unidade", "quantidade_por_unidade", "preco_por_unidade", "data_producao", "marca"]
        read_only_fields = ['id']



