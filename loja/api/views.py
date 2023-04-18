#from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from loja.models import Utilizador, Consumidor, Fornecedor, UnidadeProducao, Veiculo
### serializers ###
from .serializers import UtilizadorSerializer, ConsumidorSerializer, ForncedorSerializer, UnidadeProducaoSerializer, VeiculoSerializer



@api_view(['GET'])  # Exemplo para as próximas views: @api_view(['GET', 'PUT' 'POST'])
def getRotas(request):
    """Todas as rotas que a API fornece

    Args:
        request (_type_): pedido http. O ficheiro urls chama a função e passa automaticamente a variável
    """
    # rotas = [
    #     ############# GETS ####################
    #     'GET /api/utilizadores/',
    #     'GET /api/utilizadores/:id',
    # ]
    rotas = {
            'GET': [
                    '/api/utilizadores/', 
                    '/api/utilizadores/:id/',
                    'api/fornecedores/',
                    'api/fornecedores/:id/',
                    'api/consumidores/',
                    'api/consumidores/:id/',
                    'api/fornecedores/:id/unidadesProducao/',
                    'api/fornecedores/:id/unidadesProducao/:id/',
                    'api/fornecedores/:id/unidadesProducao/:id/veiculos/',
                    'api/fornecedores/:id/unidadesProducao/:id/veiculos/:id',
                    ]
            }
    return Response(rotas)


@api_view(['GET']) 
def getUtilizadores(request):
    utilizadores = Utilizador.objects.all() # lista de objetos. uma queryset
    respostaDevolver = UtilizadorSerializer(utilizadores, many=True) # many --> Se for um objeto a serializar é False. Se for mais que um é True.
    # FIXME retirar comentários para entender o que é o UtilizadorSerializer devolve.
    print("####################################")
    print("\n\n\n\n\n")
    print(respostaDevolver)
    print("\n\n\n\n\n")
    print("####################################")
    return Response(respostaDevolver.data)




@api_view(['GET']) 
def getUtilizador(request, idUtilizador):
    utilizadores = Utilizador.objects.get(id=idUtilizador) # um objeto
    respostaDevolver = UtilizadorSerializer(utilizadores, many=False) # many --> Se for um objeto a serializar é False, retorna um só objeto
                                                                     # . Se for mais que um objeto é True.
    # FIXME retirar comentários para entender o que é o UtilizadorSerializer devolve.
    # print("####################################")
    # print("\n\n\n\n\n")
    # print(respostaDevolver)
    # print("\n\n\n\n\n")
    # print("####################################")
    return Response(respostaDevolver.data)

###############################
@api_view(['GET'])
def getConsumidores(request):
    consumidores = Consumidor.objects.all()
    respostaDevolver = ConsumidorSerializer(consumidores, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getConsumidor(request, idConsumidor):
    consumidor = Consumidor.objects.get(id=idConsumidor)
    respostaDevolver = ConsumidorSerializer(consumidor, many=False)
    return Response(respostaDevolver.data)
###################################################3
@api_view(['GET'])
def getFornecedores(request):
    fornecedores = Fornecedor.objects.all()
    respostaDevolver = ForncedorSerializer(fornecedores, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getFornecedor(request, idFornecedor):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    respostaDevolver = ForncedorSerializer(fornecedor, many=False)
    return Response(respostaDevolver.data)
################################


@api_view(['GET'])
def getVeiculos(request, idFornecedor, idUnidadeProducao):

    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    veiculos = unidadeProducao.veiculo_set.all()
    respostaDevolver = VeiculoSerializer(veiculos, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getVeiculo(request, idVeiculo, idFornecedor, idUnidadeProducao):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    veiculo = unidadeProducao.veiculo_set.get(id=idVeiculo)
    respostaDevolver = VeiculoSerializer(veiculo, many=False)
    return Response(respostaDevolver.data)

########################


@api_view(['GET'])
def getUPs(request, idFornecedor):

    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadesProducao = fornecedor.unidades_producao.all()
    respostaDevolver = UnidadeProducaoSerializer(unidadesProducao, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getUP(request, idFornecedor, idUnidadeProducao):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    respostaDevolver = UnidadeProducaoSerializer(unidadeProducao, many=False)
    return Response(respostaDevolver.data)