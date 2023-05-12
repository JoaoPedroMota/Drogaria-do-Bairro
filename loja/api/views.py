### APP loja #####
### models.py ###
from loja.models import Utilizador, Consumidor, Fornecedor, UnidadeProducao, Veiculo
#### DJANGO ######
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
##### REST FRAMEWORK #####
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions
from rest_framework.serializers import CharField
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
#### DENTRO DA APP #####
### serializers.py ###
from .serializers import UtilizadorSerializer, ConsumidorSerializer, ForncedorSerializer, UnidadeProducaoSerializer, VeiculoSerializer
### permissions.py ###
from .permissions import IsOwnerOrReadOnly


@api_view(['GET'])  # Exemplo para as próximas views: @api_view(['GET', 'PUT' 'POST'])
def getRotas(request, format=None):
    """Todas as rotas que a API fornece
    Args:
    request: pedido http. O ficheiro urls chama a função e passa automaticamente a variável
    """
    # rotas = [
    #     ############# GETS ####################
    #     'GET /api/utilizadores/',
    #     'GET /api/utilizadores/:id',
    # ]
    rotas = {
            'GET': [
                    '/api/utilizadores/', 
                    '/api/utilizadores/:username/',
                    '/api/fornecedores/',
                    '/api/fornecedores/:id/',
                    '/api/consumidores/',
                    '/api/consumidores/:id/',
                    '/api/fornecedores/:id/unidadesProducao/',
                    '/api/fornecedores/:id/unidadesProducao/:id/',
                    '/api/fornecedores/:id/unidadesProducao/:id/veiculos/',
                    '/api/fornecedores/:id/unidadesProducao/:id/veiculos/:id',
                    ]
            }
    return Response(rotas)

#################################################

@method_decorator(csrf_protect, name='dispatch')
class UtilizadoresList(APIView):
    """
    Devolve todos os utilizadores presentes na BD ou cria um novo utilizador
    """
    #parser_classes = (MultiPartParser, FormParser)
    def get(self, request, format=None):
        utilizadores = Utilizador.objects.all()
        serializar = UtilizadorSerializer(utilizadores, many=True)
        return Response(serializar.data)
    def post(self, request, format=None):
        request.data['username'] = request.data['username'].lower()
        utilizador = UtilizadorSerializer(data=request.data)
        if utilizador.is_valid():
            utilizador_temp = utilizador.save()
            if utilizador_temp.tipo_utilizador == "C":
                Consumidor.objects.create(utilizador=utilizador_temp)
                print("Sou consumidor")
            else:
                Fornecedor.objects.create(utilizador=utilizador_temp)
                print("Sou fornecedor")
            return Response(utilizador.data, status=status.HTTP_201_CREATED)
        return Response(utilizador.errors, status=status.HTTP_400_BAD_REQUEST)


 

@method_decorator(csrf_protect, name='dispatch')
class UtilizadoresDetail(APIView):
    """
    Devolve, atualiza ou apaga uma instância de Utilizador
    """
    #parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            return Utilizador.objects.get(username=identifier)
        except Utilizador.DoesNotExist:
            raise Http404
    def get(self, request, idUtilizador, format=None):
        utilizador = self.get_object(idUtilizador)
        serializar = UtilizadorSerializer(utilizador, many=False)
        return Response(serializar.data)
    
    def put(self, request, idUtilizador, format=None):
        utilizador = self.get_object(idUtilizador)
        deserializar = UtilizadorSerializer(utilizador, data = request.data)
        if deserializar.is_valid():
            deserializar.save()
            return Response(deserializar.data)
        return Response(deserializar.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request, idUtilizador, format=None):
        # if 'password' not in request.data:
        #     return Response("Password Required", status=status.HTTP_400_BAD_REQUEST)
        # password = request.data['password']
        utilizador = self.get_object(idUtilizador)
        # if not check_password(password, utilizador.password):
        #     return Response("Password is incorrect", status=status.HTTP_401_UNAUTHORIZED)
        utilizador.delete()
        if "@" in idUtilizador:
            mensagem = f"Utilizador com o email '{utilizador.email}' foi apagado com sucesso!"
        else:
             mensagem = f"Utilizador com o username '{utilizador.username}' foi apagado com sucesso!"
        return Response(mensagem,status=status.HTTP_204_NO_CONTENT)


# class UtilizadoresViewSet(ViewSet):
#     """
#     Devolve todos os utilizadores presentes na BD ou cria um novo utilizador
#     """
#     @action(detail=False, methods=['get'])
#     def list(self, request, *args, **kwargs):
#         utilizadores = Utilizador.objects.all()
#         serializar = UtilizadorSerializer(utilizadores, many=True)
#         return Response(serializar.data)

#     @action(detail=False, methods=['post'])
#     def create(self, request, *args, **kwargs):
#         request.data['username'] = request.data['username'].lower()
#         utilizador = UtilizadorSerializer(data=request.data)
#         if utilizador.is_valid():
#             utilizador_temp = utilizador.save()
#             if utilizador_temp.tipo_utilizador == "C":
#                 Consumidor.objects.create(utilizador=utilizador_temp)
#                 print("Sou consumidor")
#             else:
#                 Fornecedor.objects.create(utilizador=utilizador_temp)
#                 print("Sou fornecedor")
#             return Response(utilizador.data, status=status.HTTP_201_CREATED)
#         return Response(utilizador.errors, status=status.HTTP_400_BAD_REQUEST)

#     """
#     Devolve, atualiza ou apaga uma instância de Utilizador
#     """
#     @action(detail=True, methods=['get', 'put', 'delete'])
#     def detail(self, request, pk=None):
#         permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
#         utilizador = self.get_object(pk)
#         if request.method == 'GET':
#             serializar = UtilizadorSerializer(utilizador, many=False)
#             return Response(serializar.data)
#         elif request.method == 'PUT':
#             deserializar = UtilizadorSerializer(utilizador, data=request.data)
#             if deserializar.is_valid():
#                 deserializar.save()
#                 return Response(deserializar.data)
#             return Response(deserializar.errors, status=status.HTTP_400_BAD_REQUEST)
#         elif request.method == 'DELETE':
#             utilizador.delete()
#             if "@" in idUtilizador:
#                 mensagem = f"Utilizador com o email '{utilizador.email}' foi apagado com sucesso!"
#             else:
#                 mensagem = f"Utilizador com o username '{utilizador.username}' foi apagado com sucesso!"
#             return Response(mensagem, status=status.HTTP_204_NO_CONTENT)

#     def get_object(self, pk):
#         try:
#             return Utilizador.objects.get(pk=pk)
#         except Utilizador.DoesNotExist:
#             raise Http404




class UnidadeProducaoList(APIView):

    def get(self, request, idFornecedor, format=None):
        unidades_producao = UnidadeProducao.objects.filter(fornecedor = idFornecedor)
        ups= UnidadeProducaoSerializer(unidades_producao, many=True)
        return Response(ups.data)
    def post(self, request, idFornecedor, formato=None):
        fornecedor = Fornecedor.objects.get(id=idFornecedor)
        if request.user.is_consumidor:
            return Response("Não pode criar uma unidade de produção. Não é um fornecedor!")
        if request.user.fornecedor != fornecedor:
            return Response("Só pode criar unidades de produção para si e não para os outros")
        request.data['fornecedor'] = fornecedor
        deserializer = UnidadeProducaoSerializer(data=request.data)
        if deserializer.is_valid():
            up_guardada = deserializer.save()
            return Response(up_guardada.data, status_code=status.HTTP_201_CREATED)
        return Response(deserializer.erros, status_code=status.HTTP_400_BAD_REQUEST)
    

class UnidadeProducaoDetail(APIView):
    def get_object(self, identifier):
        try:
            return UnidadeProducao.objects.get(id=identifier)
        except UnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request, idFornecedor, idUnidadeProducao,format=None):
        unidade_producao = self.get_object(idUnidadeProducao)
        ups= UnidadeProducaoSerializer(unidade_producao, many=False)
        return Response(ups.data)
    def put(self, request, idFornecedor, idUnidadeProducao, format=None):
        fornecedor = Fornecedor.objects.get(id=idFornecedor)
        if request.user.is_consumidor:
            return Response("Não pode criar uma unidade de produção. Não é um fornecedor!")
        if request.user.fornecedor != fornecedor:
            return Response("Só pode criar unidades de produção para si e não para os outros")
        up = self.get_object(idUnidadeProducao)
        deserializer = UnidadeProducaoSerializer(up, data=request.data)
        if deserializer.is_valid():
            deserializer.save()
            return Response(deserializer.data, status=status.HTTP_200_OK)
        return Response(deserializer.erros,status=status.HTTP_400_BAD_REQUEST)





###############################
class ConsumidoresList(APIView):
    """
    Devolve todos os consumidores presentes na BD
    """
    def get(self, request, format=None):
        consumidores = Consumidor.objects.all()
        serializar = ConsumidorSerializer(consumidores, many=True)
        return Response(serializar.data)

@method_decorator(csrf_protect, name='dispatch')
class ConsumidoresDetail(APIView):
    """
    Devolve  uma instância de Consumidor
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            utilizador_temp = Utilizador.objects.get(username=identifier)
            return Consumidor.objects.get(utilizador=utilizador_temp)
        except Consumidor.DoesNotExist:
            raise Http404
    def get(self, request, username, format=None):
        consumidor = self.get_object(username)
        serializar = ConsumidorSerializer(consumidor, many=False)
        return Response(serializar.data)






############### FORNECEDORES ################
class FornecedoresList(APIView):
    """
    Devolve todos os fornecedores presentes na BD
    """
    def get(self, request, format=None):
        print("\n\n\nCheguei aqui\n\n\n")
        fornecedores = Fornecedor.objects.all()
        print("\n\n\nCheguei aqui 2\n")
        print(fornecedores, "\n\n\n")
        serializar = ForncedorSerializer(fornecedores, many=True)
        print("\n\n\nCheguei aqui 3\n\n\n")
        return Response(serializar.data)

@method_decorator(csrf_protect, name='dispatch')
class FornecedoresDetail(APIView):
    """
    Devolve  uma instância de Fornecedor
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            utilizador_temp = Utilizador.objects.get(username=identifier)
            return Fornecedor.objects.get(utilizador=utilizador_temp)
        except Fornecedor.DoesNotExist:
            raise Http404
    def get(self, request, username, format=None):
        fornecedor = self.get_object(username)
        serializar = ForncedorSerializer(fornecedor, many=False)
        return Response(serializar.data)
    
###################################################################################################3


@api_view(['GET'])
def getVeiculos(request, username, idUnidadeProducao, format=None):
    utilizador_temp = Utilizador.objects.get(username=username)
    fornecedor = Fornecedor.objects.get(utilizador=utilizador_temp)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    veiculos = unidadeProducao.veiculos.all()
    respostaDevolver = VeiculoSerializer(veiculos, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getVeiculo(request, idVeiculo, idFornecedor, idUnidadeProducao, format=None):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    veiculo = unidadeProducao.veiculos.get(id=idVeiculo)
    respostaDevolver = VeiculoSerializer(veiculo, many=False)
    return Response(respostaDevolver.data)

########################


@api_view(['GET'])
def getUPs(request, idFornecedor, format=None):

    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadesProducao = fornecedor.unidades_producao.all()
    respostaDevolver = UnidadeProducaoSerializer(unidadesProducao, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getUP(request, idFornecedor, idUnidadeProducao, format=None):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    respostaDevolver = UnidadeProducaoSerializer(unidadeProducao, many=False)
    return Response(respostaDevolver.data)