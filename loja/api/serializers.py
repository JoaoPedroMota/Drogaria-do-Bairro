from rest_framework.serializers import ModelSerializer, Field, SerializerMethodField, ValidationError
from rest_framework.fields import ImageField
#### MODELOS ####
from loja.models import Utilizador, Consumidor, UnidadeProducao, Fornecedor, Veiculo, Produto, Categoria, Carrinho, ProdutosCarrinho, ProdutoUnidadeProducao

#######
from django_countries.fields import CountryField
from django_countries.serializers import CountryFieldMixin
from django_countries import countries
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password as django_validate_password
from rest_framework.serializers import CharField

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
        #fields = ['username', 'password', 'first_name', 'last_name', 'email', 'pais', 'cidade', 'nome', 'telemovel', 'tipo_utilizador']
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'pais', 'cidade', 'nome', 'telemovel', 'tipo_utilizador', 'imagem_perfil']
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
        read_only_fields = ['fornecedor']
    ####def create(self, validated_data):

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
        fields= ['nome']
class ProdutoSerializer(ModelSerializer):
    categoria = CategoriaProduto(read_only=True)
    class Meta:
        model = Produto
        fields = ['id','nome', 'categoria']
        
        
        
        
class CarrinhoSerializer(ModelSerializer):
    consumidor = ConsumidorSerializer()
    class Meta:
        model = Carrinho
        fields = ['id','nome', 'consumidor']




class ProdutoUnidadeProducaoSerializer(ModelSerializer):
    # produto = ProdutoSerializer()
    # unidade_producao = UnidadeProducaoSerializer()
    
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ["id","produto", "unidade_producao", "stock","descricao", "unidade_medida", "preco_a_granel", "unidade_Medida_Por_Unidade", "quantidade_por_unidade", "preco_por_unidade", "data_producao", "marca"]
        read_only_fields = ['id']


 
        
class ProdutosCarrinhoSerializer(ModelSerializer):
    carrinho = CarrinhoSerializer()
    produto = ProdutoUnidadeProducaoSerializer
    class Meta:
        model= ProdutosCarrinho
        fields= ["carrinho", "produto", "quantidade"]