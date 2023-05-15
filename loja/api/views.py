### APP loja #####
### models.py ###
from loja.models import Utilizador, Consumidor, Fornecedor, UnidadeProducao, Veiculo, Categoria, Produto, Carrinho, ProdutoUnidadeProducao
#### DJANGO ######
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
##### REST FRAMEWORK #####
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.serializers import CharField
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from decimal import Decimal
#### DENTRO DA APP #####
### serializers.py ###
from .serializers import UtilizadorSerializer, ConsumidorSerializer, FornecedorSerializer, ProdutoSerializer,UnidadeProducaoSerializer, VeiculoSerializer, CategoriaSerializer, ProdutoUnidadeProducaoSerializer
### permissions.py ###
from .permissions import IsOwnerOrReadOnly, IsFornecedorOrReadOnly, IsFornecedorAndOwnerOrReadOnly
####

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






#@method_decorator(csrf_protect, name='dispatch')
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
        print("Método:", request.method)
        request.data['username'] = request.data['username'].lower()
        utilizador = UtilizadorSerializer(data=request.data)
        if utilizador.is_valid():
            utilizador_temp = utilizador.save()
            if utilizador_temp.tipo_utilizador == "C":
                cons = Consumidor.objects.create(utilizador=utilizador_temp)
                carrinho = Carrinho.objects.create(consumidor=cons)
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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
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

class UnidadeProducaoList(APIView):
    permission_classes = [IsFornecedorOrReadOnly]

    def get(self, request, idFornecedor, format=None):
        unidades_producao = UnidadeProducao.objects.filter(fornecedor = idFornecedor)
        ups= UnidadeProducaoSerializer(unidades_producao, many=True)
        return Response(ups.data)
    def post(self, request, idFornecedor, formato=None):
        fornecedor = Fornecedor.objects.get(id=idFornecedor)
        if request.user.is_consumidor:
            return Response("Não pode criar uma unidade de produção. Não é um fornecedor!")
        if request.user.fornecedor != fornecedor:
            return Response("Só pode criar unidades de produção para si e não para os outros.")
        request.data['fornecedor'] = fornecedor
        deserializer = UnidadeProducaoSerializer(data=request.data)
        if deserializer.is_valid():
            up_guardada = deserializer.save()
            return Response(up_guardada.data, status_code=status.HTTP_201_CREATED)
        return Response(deserializer.erros, status_code=status.HTTP_400_BAD_REQUEST)
    

class UnidadeProducaoDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsFornecedorAndOwnerOrReadOnly]#, IsFornecedorOrReadOnly
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
        if request.user.is_fornecedor:
            if request.user.fornecedor != fornecedor:
                return Response("Só pode editar unidades de produção para si e não para os outros")
            up = self.get_object(idUnidadeProducao)
            deserializer = UnidadeProducaoSerializer(up, data=request.data)
            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_200_OK)
            return Response(deserializer.erros,status=status.HTTP_400_BAD_REQUEST)

            
        
    def delete(self, request, idFornecedor, idUnidadeProducao, format=None):
        Fornecedor = Fornecedor.objects.get(id=idFornecedor)
        if request.user.is_consumidor:
            return Response("Não pode criar uma unidade de produção. Não é um fornecedor!")
        if request.user.fornecedor != fornecedor:
            return Response("Só pode criar unidades de produção para si e não para os outros")
        up = self.get_object(idUnidadeProducao)
        up.delete()
        return Response(f"Unidade de produção '{up.nome}' apagada com sucesso!",status=status.HTTP_204_NO_CONTENT)





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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            return Consumidor.objects.get(pk=identifier)
        except Consumidor.DoesNotExist:
            raise Http404
    def get(self, request, idConsumidor, format=None):
        consumidor = self.get_object(idConsumidor)
        serializar = ConsumidorSerializer(consumidor, many=False)
        return Response(serializar.data)






############### FORNECEDORES ################
class FornecedoresList(APIView):
    """
    Devolve todos os fornecedores presentes na BD
    """
    def get(self, request, format=None):
        fornecedores = Fornecedor.objects.all()
        serializar = FornecedorSerializer(fornecedores, many=True)
        return Response(serializar.data)

@method_decorator(csrf_protect, name='dispatch')
class FornecedoresDetail(APIView):
    """
    Devolve  uma instância de Fornecedor
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            return Fornecedor.objects.get(pk=identifier)
        except Fornecedor.DoesNotExist:
            raise Http404
    def get(self, request, idFornecedor, format=None):
        fornecedor = self.get_object(idFornecedor)
        serializar = FornecedorSerializer(fornecedor, many=False)
        return Response(serializar.data)
    
###################################################################################################3
###CATEGORIA
class CategoriaList(APIView):
    """
    Devolve todas as categorias da loja
    """
    def get(self, request, format=None):
        categorias = Categoria.objects.all()
        serializar = CategoriaSerializer(categorias, many=True)
        return Response(serializar.data, status=status.HTTP_200_OK)
class CategoriaDetail(APIView):
    """
    Devolve uma categoria
    """
    def get_object(self, identifier):
        try:
            return Categoria.objects.get(slug=identifier)
        except Categoria.DoesNotExist:
            return Http404
    def get(self, request, slug, format=None):
        categoria = self.get_object(slug)
        serializar = CategoriaSerializer(categoria, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)
##############################################################

class ProdutoList(APIView):
    """
    Devolve todos os produtos da loja
    """
    permission_classes= [IsFornecedorOrReadOnly,IsAuthenticatedOrReadOnly]
    def get(self, request, format=None):
        produtos = Produto.objects.all()
        serializar = ProdutoSerializer(produtos, many=True)
        return Response(serializar.data, status=status.HTTP_200_OK)
    def post(self, request, format=None):
        request.data['slug'] = request.data['slug']
        produto = ProdutoSerializer(data=request.data)
        if produto.is_valid():
            produto_temp = produto.save()
            return Response(produto_temp.data, status=status.HTTP_201_CREATED)
        return Response(produto.errors, status=status.HTTP_400_BAD_REQUEST)


class ProdutoDetail(APIView):
    """
    Devolve um produto existente na loja
    """
    def get_object(self, identifier):
        try:
            return Produto.objects.get(nome=identifier)
        except Produto.DoesNotExist:
            return Http404
    def get(self, request, slug, format=None):
        produto = self.get_object(slug)
        serializar = ProdutoSerializer(produto, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)



class ProdutoUnidadeProducaoList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsFornecedorAndOwnerOrReadOnly]

    def get_categoria(self, identifier):
        try:
            return Categoria.objects.get(nome=identifier)
        except Categoria.DoesNotExist:
            raise Http404

    def get_unidade_producao(self, identifierFornecedor, identifierUP):
        try:
            fornecedor = Fornecedor.objects.get(id=identifierFornecedor)
            try:
                return UnidadeProducao.objects.get(Q(fornecedor=fornecedor) & Q(id=identifierUP))
            except UnidadeProducao.DoesNotExist:
                raise Http404
        except Fornecedor.DoesNotExist:
            raise Http404
        
    def get(self, request, idFornecedor, idUnidadeProducao, format=None):
        up = self.get_unidade_producao(idFornecedor, idUnidadeProducao)
        proUP = ProdutoUnidadeProducao.objects.filter(unidade_producao=up)
        serializar = ProdutoUnidadeProducaoSerializer(proUP, many=True)
        return Response(serializar.data, status=status.HTTP_200_OK)


    def post(self, request, idFornecedor,idUnidadeProducao, format=None):
        fornecedor = Fornecedor.objects.get(id=idFornecedor)
        unidadeProducao = UnidadeProducao.objects.get(id=idUnidadeProducao)
        if request.data['unidade_producao'] != idUnidadeProducao:
            return Response(f'Não pode adicionar produtos a outra unidade de produção que não a atual. Você está na unidade de produção:{unidadeProducao.nome}. Use o id {unidadeProducao.id}')
        produto_request = request.data['produto']
        # nome_produto = produto_request['nome']
        # produto, created = Produto.objects.get_or_create(nome=nome_produto)
        # if created:
        #     nome_categoria = produto_request['categoria']['nome']
        #     categoria = self.get_categoria(nome_categoria)
        #     produto.categoria = categoria
        #     produto.save()

        serializar = ProdutoUnidadeProducaoSerializer(data=request.data)
        if serializar.is_valid():
            serializar.save()
            return Response(serializar.data, status=status.HTTP_201_CREATED)
        return Response(serializar.errors, status=status.HTTP_400_BAD_REQUEST)


class ProdutoUnidadeProducaoAll(APIView):
    """Devolve todos os produtos que estão associados a uma unidade de produção. Mostra os produtos quer estejam
    disponiveis(com stock) quer não estejam 

    Args:
        APIView (_type_): _description_
    """
    def get(self, request):
        produtos = ProdutoUnidadeProducao.objects.all()
        serializer = ProdutoUnidadeProducaoSerializer(produtos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProdutoUnidadeProducaoEmStock(APIView):
    """Devolve todos os produtos que estão associados a uma unidade de produção. Mostra os produtos quer estejam
    disponiveis(com stock) quer não estejam 

    Args:
        APIView (_type_): _description_
    """
    def get(self, request):
        produtos = ProdutoUnidadeProducao.objects.filter(stock__gt=Decimal(0))
        serializer = ProdutoUnidadeProducaoSerializer(produtos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def getVeiculos(request, idFornecedor, idUnidadeProducao, format=None):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
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