from rest_framework.serializers import ModelSerializer, Field, SerializerMethodField

#### MODELOS ####
from loja.models import Utilizador, Consumidor, UnidadeProducao, Fornecedor, Veiculo
from django_countries.fields import CountryField


class campoPaisSerializador(Field):
    def to_representation(self, value):
        if value is not None:
            return value.code,

        return None

    def to_internal_value(self, data):
        if data is not None:
            return CountryField().to_python(data)
        return None


class UtilizadorSerializer(ModelSerializer):
    pais = campoPaisSerializador()
    tipo_utilizador_api = SerializerMethodField()
    class Meta:
        model = Utilizador
        fields = ['id', 'username', 'first_name', 'last_name', 'email','pais' ,'cidade', 'nome', 'telemovel', 'tipo_utilizador_api']
        
        
    def get_tipo_utilizador_api(self, objeto):
        return dict(Utilizador.TIPO_UTILIZADOR).get(objeto.tipo_utilizador)
    
    
    
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