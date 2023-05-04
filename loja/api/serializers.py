from rest_framework.serializers import ModelSerializer, Field, SerializerMethodField, ValidationError

#### MODELOS ####
from loja.models import Utilizador, Consumidor, UnidadeProducao, Fornecedor, Veiculo
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

class UtilizadorSerializer(CountryFieldMixin, ModelSerializer):
    pais = campoPaisSerializador()
    tipo_utilizador = TipoUtilizadorField()
    password = CharField(write_only=True, required=False)
    nome = CharField(read_only=True)

    def create(self, validated_data):
        if 'password' not in validated_data:
            raise ValidationError("Password is required")
        if 'tipo_utilizador' not in validated_data:
            raise ValidationError("tipo_utilizador is required")

        validated_data['username'] = validated_data['username'].lower()
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
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'pais', 'cidade', 'nome', 'telemovel', 'tipo_utilizador']
        extra_kwargs = {'password': {'required': True}}
    

class ConsumidorSerializer(ModelSerializer):
    class Meta:
        model = Consumidor
        fields = '__all__'
        
        
        
class ForncedorSerializer(ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = ['id','utilizador', 'descricao']
        
        
class UnidadeProducaoSerializer(ModelSerializer):
    tipo_unidade_api = SerializerMethodField()
    class Meta:
        model = UnidadeProducao
        fields = ['id','nome', 'fornecedor', 'pais', 'cidade', 'morada', 'tipo_unidade_api']
    def get_tipo_unidade_api(self, objeto):
        return dict(UnidadeProducao.TIPO_UNIDADE).get(objeto.tipo_unidade)
    
    
class VeiculoSerializer(ModelSerializer):
    tipo_veiculo_api = SerializerMethodField()
    estado_veiculo_api = SerializerMethodField()
    class Meta:
        model = Veiculo
        fields = ['id','nome', 'unidadeProducao', 'tipo_veiculo_api', 'estado_veiculo_api']
    def get_tipo_veiculo_api(self, objeto):
        return dict(Veiculo.TIPO_VEICULO).get(objeto.tipo_veiculo)
    def get_estado_veiculo_api(self, objeto):
        return dict(Veiculo.ESTADO_VEICULO).get(objeto.estado_veiculo)