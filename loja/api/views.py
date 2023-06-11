### APP loja #####
### models.py ###
from loja.models import *
from .utilidades_api import categorias_nao_pai
#### DJANGO ######
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from django.db import transaction
##### REST FRAMEWORK #####
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.serializers import CharField
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from decimal import Decimal
#### DENTRO DA APP #####
### serializers.py ###
from .serializers import *
### permissions.py ###
from .permissions import *
####
from decimal import Decimal
import phonenumbers
from datetime import timedelta, datetime
from django.utils import timezone







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







#@method_decorator(csrf_protect, name='dispatch')
class UtilizadoresList(APIView):
    """
    Devolve todos os utilizadores presentes na BD ou cria um novo utilizador
    """
    #parser_classes = (MultiPartParser, FormParser)
    def get(self, request, format=None):
        if request.user.is_superuser:
            utilizadores = Utilizador.objects.all()
            serializar = UtilizadorSerializer(utilizadores, many=True)
            return Response(serializar.data)
        else:
            return Response({"details":"Não tem autorização para aceder a estes dados"}, status=status.HTTP_403_FORBIDDEN)
    def post(self, request, format=None):
        request.data['username'] = request.data['username'].lower()
        utilizador = UtilizadorSerializer(data=request.data)
        with transaction.atomic():
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
    permission_classes = [IsOwner] # , IsAuthenticated]
    def get_object(self, identifier):
        try:
            return Utilizador.objects.get(username=identifier)
        except Utilizador.DoesNotExist:
            raise Http404
    def get(self, request, username, format=None):
        utilizador = self.get_object(username)
        serializar = UtilizadorSerializer(utilizador, many=False)
        return Response(serializar.data)
    
    def put(self, request, username, format=None):
        utilizador = self.get_object(username)
        deserializar = UtilizadorSerializer(utilizador, data = request.data)
        if deserializar.is_valid():
            deserializar.save()
            return Response(deserializar.data)
        return Response(deserializar.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request, username, format=None):
        # if 'password' not in request.data:
        #     return Response("Password Required", status=status.HTTP_400_BAD_REQUEST)
        # password = request.data['password']
        utilizador = self.get_object(username)
        # if not check_password(password, utilizador.password):
        #     return Response("Password is incorrect", status=status.HTTP_401_UNAUTHORIZED)
        utilizador.delete()
        mensagem = f"Utilizador com o username '{utilizador.username}' foi apagado com sucesso!"
        return Response(mensagem,status=status.HTTP_204_NO_CONTENT)

class UnidadeProducaoList(APIView):
    permission_classes = [IsFornecedorOrReadOnly]
    def get_object(self, identifier):
        try:
            utilizador_temp = Utilizador.objects.get(username=identifier)
            try:
                fornecedor_temp = Fornecedor.objects.get(utilizador=utilizador_temp)
                try:
                    return UnidadeProducao.objects.filter(fornecedor = fornecedor_temp)
                except UnidadeProducao.DoesNotExist:
                    raise Http404
            except Fornecedor.DoesNotExist:
                raise Http404
        except:
            raise Http404
    def get(self, request, username, format=None):
        UPs = self.get_object(username)
        if UPs.exists():
            serializar = UnidadeProducaoSerializer(UPs, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data, status=status.HTTP_200_OK)
    def post(self, request, username, formato=None):
        utilizador = Utilizador.objects.get(username=username)
        fornecedor = Fornecedor.objects.get(utilizador=utilizador)
        if request.user.is_consumidor:
            return Response("Não pode criar uma unidade de produção. Não é um fornecedor!")
        if request.user.fornecedor != fornecedor:
            return Response("Só pode criar unidades de produção para si e não para os outros.")
        deserializer = UnidadeProducaoSerializer(data=request.data)
        if deserializer.is_valid():
            up_guardada = deserializer.save(fornecedor=fornecedor)
            return Response(deserializer.data, status=status.HTTP_201_CREATED)
        return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UnidadeProducaoDetailSoInfo(APIView):
    def get_object(self, identifier):
        try:
            return UnidadeProducao.objects.get(id=identifier)
        except UnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request, id):
        up = self.get_object(id)
        upSerializer = UnidadeProducaoSerializer(up, many=False)
        return Response(upSerializer.data, status=status.HTTP_200_OK)





class UnidadeProducaoDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsFornecedorAndOwnerOrReadOnly]#, IsFornecedorOrReadOnly
    def get_object(self, identifier, username):
        try:
            utilizador = Utilizador.objects.get(username = username)
            try:
                fornecedor = Fornecedor.objects.get(utilizador=utilizador)
                try:
                    return UnidadeProducao.objects.get(id=identifier, fornecedor=fornecedor)
                except UnidadeProducao.DoesNotExist:
                    raise Http404
            except Fornecedor.DoesNotExist:
                raise Http404 
        except Utilizador.DoesNotExist:
            raise Http404
    def get(self, request, username, idUnidadeProducao,format=None):
        unidade_producao = self.get_object(idUnidadeProducao, username)
        ups= UnidadeProducaoSerializer(unidade_producao, many=False)
        return Response(ups.data, status=status.HTTP_200_OK)
    def put(self, request, username, idUnidadeProducao, format=None):
        user = Utilizador.objects.get(username=username)
        fornecedor = user.fornecedor
        if request.user.is_consumidor:
            return Response("Não pode criar uma unidade de produção. Não é um fornecedor!", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.is_fornecedor:
            if request.user.fornecedor != fornecedor:
                return Response("Só pode editar unidades de produção para si e não para os outros", status=status.HTTP_400_BAD_REQUEST)
            up = self.get_object(idUnidadeProducao, username)
            deserializer = UnidadeProducaoSerializer(up, data=request.data)
            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_200_OK)
            return Response(deserializer.errors,status=status.HTTP_400_BAD_REQUEST)

            
        
    def delete(self, request, username, idUnidadeProducao, format=None):
        user = Utilizador.objects.get(username=username)
        fornecedor = user.fornecedor
        if request.user.is_consumidor:
            return Response("Não pode apagar uma unidade de produção. Não é um fornecedor!")
        if request.user.fornecedor != fornecedor:
            return Response("Só pode apagar as suas unidades de produção e não as dos outros")
        up = self.get_object(idUnidadeProducao, username)
        up.delete()
        return Response(f"Unidade de produção '{up.nome}' apagada com sucesso!",status=status.HTTP_204_NO_CONTENT)





###############################
class ConsumidoresList(APIView):
    """
    Devolve todos os consumidores presentes na BD
    """
    def get(self, request, format=None):
        consumidores = Consumidor.objects.all()
        if consumidores.count()>1:
            serializar = ConsumidorSerializer(consumidores, many=True)
        elif consumidores.count()==1:
            serializar = ConsumidorSerializer(consumidores, many=False)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializar.data)

@method_decorator(csrf_protect, name='dispatch')
class ConsumidoresDetail(APIView):
    """
    Devolve  uma instância de Consumidor
    """
    #permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            utilizador_temp = Utilizador.objects.get(username=identifier)
            try:
                return Consumidor.objects.get(utilizador=utilizador_temp)
            except Consumidor.DoesNotExist:
                raise Http404
        except Utilizador.DoesNotExist:
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
            utilizador_temp = Utilizador.objects.get(username=identifier)
            try:
                return Fornecedor.objects.get(utilizador=utilizador_temp)
            except Fornecedor.DoesNotExist:
                raise Http404
        except:
            raise Http404
    def get(self, request, username, format=None):
        fornecedor = self.get_object(username)
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
            return Categoria.objects.get(id=identifier)
        except Categoria.DoesNotExist:
            print("ERRO!")
            return Http404
    def get(self, request, id, format=None):
        categoria = self.get_object(id)
        serializar = CategoriaSerializer(categoria, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)
##############################################################

class CategoriaDetailNome(APIView):
    """
    Devolve uma categoria, mas pelo nome
    """
    def get_object(self, identifier):
        try:
            return Categoria.objects.get(nome=identifier)
        except Categoria.DoesNotExist:
            return Http404
    def get(self, request, nome, format=None):
        categoria = self.get_object(nome)
        serializar = CategoriaSerializer(categoria, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)



class ProdutoList(APIView):
    """
    Devolve todos os produtos da loja
    """
    permission_classes= [IsFornecedorOrReadOnly]#,IsAuthenticatedOrReadOnly]
    def get(self, request, format=None):
        if 'q' in request.data:
            if request.data['q'] != '':
                criterio_pesquisa = request.data['q']
                produtos = Produto.objects.filter(
                    Q(nome__icontains=criterio_pesquisa) |
                    Q(categoria__nome__icontains=criterio_pesquisa)
                    )
                if produtos.exists():
                    serializar = ProdutoSerializer(produtos, many=True)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(serializar.data, status= status.HTTP_200_OK)
            else:
                produtos = Produto.objects.all()
                if produtos.exists():
                    serializar = ProdutoSerializer(produtos, many=True)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(serializar.data, status=status.HTTP_200_OK)
        else:
            produtos = Produto.objects.all()
            serializar = ProdutoSerializer(produtos, many=True)
            return Response(serializar.data, status=status.HTTP_200_OK)
        
    def post(self, request, format=None):
        #request.data['slug'] = request.data['slug']
        produto = ProdutoSerializerRequest(data=request.data)
        if produto.is_valid():
            produto_temp = produto.save()
            resposta_produto_serializer = ProdutoSerializer(produto_temp, many=False)
            return Response(resposta_produto_serializer.data, status=status.HTTP_201_CREATED)
        #print("\n\n\n\n", produto.errors, "\n\n\n\n\n")
        print(produto.errors)
        return Response({'detail': produto.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProdutoDetail(APIView):
    """
    Devolve um produto existente na loja
    """
    def get_object(self, identifier):
        try:
            return Produto.objects.get(nome=identifier)
        except Produto.DoesNotExist:
            return Http404
    def get(self, request, nome, format=None):
        produto = self.get_object(nome)
        serializar = ProdutoSerializer(produto, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)


class ProdutoDetailID(APIView):
    """
    Devolve um produto na loja, mas procura por um id
    """
    def get_object(self, identifier):
        try:
            return Produto.objects.get(id=identifier)
        except Produto.DoesNotExist:
            return Http404
    def get(self, request, id, format=None):
        produto = self.get_object(id)
        serializar = ProdutoSerializer(produto, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)

class ProdutoUnidadeProducaoList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsFornecedorAndOwnerOrReadOnly]
    def get_produtos_up(self, username, identifierUP):
        try:
            user = Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404("Utilizador não encontrado")

        try:
            fornecedor = user.fornecedor
        except Fornecedor.DoesNotExist:
            raise Http404("O username introduzido não corresponde a um fornecedor")

        try:
            
            up = UnidadeProducao.objects.get(Q(fornecedor=fornecedor) & Q(id=identifierUP))
        except UnidadeProducao.DoesNotExist:
            raise Http404(f"O fornecedor introduzido não tem nenhuma Unidade de Produção com o id {identifierUP}")

        try:
            produtos_up = ProdutoUnidadeProducao.objects.filter(unidade_producao=up)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404("A unidade de produção escolhida não contém produtos associados")
        else:
            return produtos_up

        
    def get(self, request, username, idUnidadeProducao, format=None):
        proUP = self.get_produtos_up(username, idUnidadeProducao)
        if proUP.exists():
            serializar = ProdutoUnidadeProducaoSerializer(proUP, many=True)
            return Response(serializar.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


    def post(self, request, username,idUnidadeProducao, format=None):
        try:
            user = Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
        try:
            fornecedor = user.fornecedor
        except Fornecedor.DoesNotExist:
            raise Http404
        try:
            unidadeProducao = UnidadeProducao.objects.get(id=idUnidadeProducao)
        except UnidadeProducao.DoesNotExist:
            raise Http404
        #print("PRINT NA API. REQUEST.DATA:",request.data)
        if int(request.data.get('unidade_producao')) != int(idUnidadeProducao):
            return Response(f'Não pode adicionar produtos a outra unidade de produção que não a atual. Você está na unidade de produção:{unidadeProducao.nome}. Use o id {unidadeProducao.id}', status=status.HTTP_400_BAD_REQUEST)
        serializar = ProdutoUnidadeProducaoSerializer(data=request.data)
        if serializar.is_valid():
            serializar.save()
            return Response(serializar.data, status=status.HTTP_201_CREATED)
        print(serializar.errors)
        return Response(serializar.errors, status=status.HTTP_400_BAD_REQUEST)



class ProdutoUnidadeProducaoDetail(APIView):
    """
    Um só produto relativo a uma unidade de produção de um dado fornecedor. 
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsFornecedorAndOwnerOrReadOnly]
    def get_object(self, identifier):
        try:
            return ProdutoUnidadeProducao.objects.get(pk=identifier)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request, username, idUnidadeProducao, idProdutoUnidadeProducao, formato=None):
        produto = self.get_object(idProdutoUnidadeProducao)
        serializarProduto = ProdutoUnidadeProducaoSerializer(produto, many=False)
        return Response(serializarProduto.data, status=status.HTTP_200_OK)
    def put(self, request, username, idUnidadeProducao, idProdutoUnidadeProducao, format=None):
        produto = self.get_object(idProdutoUnidadeProducao)
        unidadeProducao = UnidadeProducao.objects.get(id=idUnidadeProducao)
        if request.data['produto'] != produto.produto.id:
            return Response(f"Não pode alterar o campo produto após a criação da associação entre o produto e uma unidade de produção. Para adicionar uma associação entre produto e unidade produção nova, crie uma nova associação com o método POST. Para remover a atual use o método DELETE")
        if request.data['unidade_producao'] != idUnidadeProducao:
            return Response(f'Não pode alterar a unidade de producao de um dado produto para outra unidade de produção. Este valor não é editável. Você está na unidade de produção:{unidadeProducao.nome}. Use o id {unidadeProducao.id}', status=status.HTTP_400_BAD_REQUEST)
        request.data['unidade_producao'] = idUnidadeProducao
        informacao = request.data
        deserializar = ProdutoUnidadeProducaoSerializer(produto, data=informacao)
        if deserializar.is_valid():
            try:
                deserializar.save()
                return Response(deserializar.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({"detail": "Já existe este produto nesta unidade de produção.", "error_code": "INTEGRITY_ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(deserializar.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, username, idUnidadeProducao, idProdutoUnidadeProducao, format=None):
        produto = self.get_object(idProdutoUnidadeProducao)
        try:
            user = Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            return Response(detail=f"Utilizador com o username: {username} não existe", status=status.HTTP_404_NOT_FOUND)
        try:
            fornecedor = Fornecedor.objects.get(utilizador=user)
        except Fornecedor.DoesNotExist:
            return Response(detail=f"Utilizador com o username: {username} não é um fornecedor", status=status.HTTP_404_NOT_FOUND)
        try:
            up = UnidadeProducao.objects.get(id=idUnidadeProducao)
        except UnidadeProducao.DoesNotExist:
            return Response(detail=f"Unidade de Produção com o id: {idUnidadeProducao} não existe", status=status.HTTP_404_NOT_FOUND)
        
        
        
        
        
        if request.user.is_consumidor:
            return Response("Não pode apagar um produto unidade de produção. Não é um fornecedor!", status=status.HTTP_404_NOT_FOUND)
        if request.user.fornecedor != fornecedor:
            return Response("Só pode apagar os seus produtos associados às suas unidades de produção e não de outros fornecedores", status=status.HTTP_404_NOT_FOUND)
        
        
        if produto is None:
             return Response({"detail": f"Produto {idProdutoUnidadeProducao} associado à unidade de produção com o id {idUnidadeProducao} não encontrado."},status=status.HTTP_404_NOT_FOUND)

        # Exclua o objeto
        produto.delete()
            
        return Response(f"Associação entre o produto {idProdutoUnidadeProducao}(Nome: {produto.produto.nome}) associado à unidade de produção: {idUnidadeProducao}(Nome da Unidade de Produção: {up.nome}) apagada com sucesso!",status=status.HTTP_204_NO_CONTENT)
        










class ProdutoUnidadeProducaoAll(APIView):
    """
    Devolve todos os produtos que estão associados a uma unidade de produção. Mostra os produtos quer estejam
    disponiveis(com stock) quer não estejam 

    Args:
        APIView (_type_): _description_
    """
    def get(self, request):
        if 'q' in request.data:
            if request.data['q'] != '':
                criterio_pesquisa = request.data['q']
                produtos = ProdutoUnidadeProducao.objects.filter(
                    Q(produto__nome__icontains=criterio_pesquisa) |
                    Q(produto__categoria__nome__icontains=criterio_pesquisa)
                    )
                if produtos.count() == 1:
                    serializer = ProdutoUnidadeProducaoSerializer(produtos, many=False)
                if produtos.count() > 1:
                    serializer = ProdutoUnidadeProducaoSerializer(produtos, many=True)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            else:
                produtos = ProdutoUnidadeProducao.objects.all()
                if produtos.count() == 1:
                    serializer = ProdutoUnidadeProducaoSerializer(produtos, many=False)
                if produtos.count() > 1:
                    serializer = ProdutoUnidadeProducaoSerializer(produtos, many=True)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            produtos = ProdutoUnidadeProducao.objects.all()
            if produtos.count() == 1:
                serializer = ProdutoUnidadeProducaoSerializer(produtos, many=False)
            if produtos.count() > 1:
                serializer = ProdutoUnidadeProducaoSerializer(produtos, many=True)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
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



class SingleProductDetails(APIView):
    def get_object(self, identifier):
        try:
            return ProdutoUnidadeProducao.objects.get(pk=identifier)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request, idProduto):
        produto = self.get_object(idProduto)
        serializador = SingleProdutoPaginaSerializer(produto, many=False)
        return Response(serializador.data, status=status.HTTP_200_OK)












@api_view(['GET'])
def getVeiculos(request, username, idUnidadeProducao, format=None):
    utilizador_temp = Utilizador.objects.get(username=username)
    fornecedor = Fornecedor.objects.get(utilizador=utilizador_temp)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    veiculos = unidadeProducao.veiculos.all()
    respostaDevolver = VeiculoSerializer(veiculos, many=True)
    return Response(respostaDevolver.data)

@api_view(['GET'])
def getVeiculo(request,username, idVeiculo, idUnidadeProducao, format=None):
    utilizador = Utilizador.objects.get(username=username)
    fornecedor = Fornecedor.objects.get(utilizador=utilizador)
    unidadeProducao = fornecedor.unidades_producao.get(pk=idUnidadeProducao)
    veiculo = unidadeProducao.veiculos.get(id=idVeiculo)
    respostaDevolver = VeiculoSerializer(veiculo, many=False)
    return Response(respostaDevolver.data)

########################


class CarrinhoList(APIView):
    """Devolve todos os ids dos carrinhos existentes e a que consumidor pertencem,

    Args:
        APIView (_type_): _description_
    """
    def get(self, rquest, format=None):
        carrinhos = Carrinho.objects.all()
        if carrinhos.count() == 1:
            serializar = CarrinhoSerializer(carrinhos, many=False)
        elif carrinhos.count() > 1:
            serializar = CarrinhoSerializer(carrinhos, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data, status=status.HTTP_200_OK)
    
class CarrinhoDetail(APIView):
    def get_object(self, instance):
        try:
            return Carrinho.objects.get(id=instance)
        except Carrinho.DoesNotExist:
            raise Http404
    def get(self, request, idCarrinho):
        carrinho = self.get_object(idCarrinho)
        serializar = CarrinhoSerializer(carrinho, many=False)
        return Response(serializar.data, status=status.HTTP_200_OK)
            

class ProdutosCarrinhoList(APIView):
    permission_classes = [IsConsumidorAndOwner, IsAuthenticatedOrReadOnly]
    def get_object(self, carrinho):
        try:
            return ProdutosCarrinho.objects.filter(carrinho=carrinho)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404

    def get_carrinho(self, username):
        try:
            utilizador_temp = Utilizador.objects.get(username=username)
            try:
                consumidor_temp = Consumidor.objects.get(utilizador = utilizador_temp)
                try:
                    return Carrinho.objects.get(consumidor=consumidor_temp)
                except Carrinho.DoesNotExist:
                    return Http404
            except Consumidor.DoesNotExist:
                raise Http404
        except Utilizador.DoesNotExist:
            raise Http404
    def get(self, request, username, format=None):

        carrinho = self.get_carrinho(username)

        itens_carrinho = self.get_object(carrinho)
        if itens_carrinho.exists():
            serializar = ProdutosCarrinhoResponseSerializer(itens_carrinho, many=True) #serializer para responder
            return Response(serializar.data,status=status.HTTP_200_OK)
        elif not itens_carrinho.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, username, format=None):
        if request.user.username != username:
            return Response({'detail':"Não tem permissão para realizar esta ação, porque não é o utilizador dono deste carrinho!"}, status=status.HTTP_401_UNAUTHORIZED)
        carrinho = self.get_carrinho(username)
        if 'carrinho' in request.data:
            if int(request.data['carrinho'])!=int(carrinho.id):
                return Response({'detail':'O ID do carrinho fornecido não corresponde ao id do carrinho do utilizador logado. Não precisa de enviar o id do carrinho, porque ele é atríbuido de acordo com o utilizador que está logado.'}, status=status.HTTP_400_BAD_REQUEST)
        serializador = ProdutosCarrinhoRequestSerializer(data=request.data)
        if serializador.is_valid():
            itemCarrinho = serializador.validated_data['produto']
            if itemCarrinho.unidade_medida in ['kg', 'g','l','ml']:
                precoKilo = itemCarrinho.preco_a_granel
                preco = Decimal(request.data['quantidade'])*precoKilo
            elif itemCarrinho.unidade_medida in ['un']:
                precoKilo = itemCarrinho.preco_por_unidade
                preco = Decimal(request.data['quantidade'])*precoKilo
            serializador.save(carrinho=carrinho, preco=preco, precoKilo=precoKilo) #atribui o carrinho da linha FIXME(carrinho = self.get_carrinho(username)), o preco e o preco por kilo/unidade
            response_serializer = ProdutosCarrinhoResponseSerializer(serializador.instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ProdutosCarrinhoDetail(APIView):
    permission_classes = [IsConsumidorAndOwner, IsAuthenticated]
    def get_object(self, cart, idProdutoCart):
        try:
            return ProdutosCarrinho.objects.get(carrinho=cart, id=idProdutoCart)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404

    def get_carrinho(self, username):
        try:
            utilizador_temp = Utilizador.objects.get(username=username)
            try:
                consumidor_temp = Consumidor.objects.get(utilizador = utilizador_temp)
                try:
                    return Carrinho.objects.get(consumidor=consumidor_temp)
                except Carrinho.DoesNotExist:
                    return Http404
            except Consumidor.DoesNotExist:
                raise Http404
        except Utilizador.DoesNotExist:
            raise Http404
    def get(self, request, username, idProdutoCart, format=None):
        """
        Devolve o produto com um dado id(id da tabela ProdutoCarrinho)

        Args:
            request (_type_): _description_
            username (_type_): _description_
            idProdutoCart (_type_): _description_
            format (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        carrinho = self.get_carrinho(username)
        item_carrinho = self.get_object(carrinho, idProdutoCart)
        if item_carrinho is not None:
            serializar = ProdutosCarrinhoResponseSerializer(item_carrinho, many=False) #serializer para responder
            return Response(serializar.data,status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Produto não encontrado no carrinho"},status=status.HTTP_404_NOT_FOUND)
    def put(self, request, username, idProdutoCart, format=None):
        carrinho = self.get_carrinho(username)
        item_carrinho = self.get_object(carrinho, idProdutoCart)
        if item_carrinho is None:
            return Response({"detail": "Produto não encontrado no carrinho"},status=status.HTTP_404_NOT_FOUND)

        # Atualize o objeto com os novos dados
        data = request.data.copy()
        
        data['produto'] = item_carrinho.produto.id
        serializer = ProdutosCarrinhoRequestSerializer(item_carrinho, data=data)
        if serializer.is_valid():
            produto = item_carrinho.produto
            if produto.unidade_medida in ['kg','g','l','ml']:
                precoKilo = produto.preco_a_granel
                preco = Decimal(request.data['quantidade']) * precoKilo
            elif produto.unidade_medida in ['un']:
                precoKilo = produto.preco_por_unidade
                preco = Decimal(request.data['quantidade']) * precoKilo
            serializer.save(preco=preco, precoKilo=precoKilo)
            
            response_serializer = ProdutosCarrinhoResponseSerializer(serializer.instance)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:   
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, username, idProdutoCart, format=None):
        carrinho = self.get_carrinho(username)
        item_carrinho = self.get_object(carrinho, idProdutoCart)
        
        if item_carrinho is None:
            return Response({"detail": "Produto não encontrado no carrinho"},status=status.HTTP_404_NOT_FOUND)

        # Exclua o objeto
        item_carrinho.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProdutosCarrinhoDetailProdutoUP(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    permission_classes = [IsConsumidorAndOwnerOrReadOnly]
    def get_object(self, cart, idProdutoUnidadeProducao):
        try:
            return ProdutosCarrinho.objects.get(carrinho=cart, produto=idProdutoUnidadeProducao)
        except ProdutosCarrinho.DoesNotExist:
            return None

    def get_carrinho(self, username):
        try:
            utilizador_temp = Utilizador.objects.get(username=username)
            try:
                consumidor_temp = Consumidor.objects.get(utilizador = utilizador_temp)
                try:
                    return Carrinho.objects.get(consumidor=consumidor_temp)
                except Carrinho.DoesNotExist:
                    raise Http404
            except Consumidor.DoesNotExist:
                raise Http404
        except Utilizador.DoesNotExist:
            raise Http404
    def get(self, request, username, idProdutoUnidadeProducao, format=None):
        carrinho = self.get_carrinho(username)
        item_carrinho = self.get_object(carrinho, idProdutoUnidadeProducao)
        if item_carrinho is not None:
            serializar = TemProdutoNoCarrinhoSerializer(item_carrinho, many=False) #serializer para responder
            return Response(serializar.data,status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Produto não encontrado no carrinho"},status=status.HTTP_404_NOT_FOUND)
    


class DetalhesEnvioList(APIView):
    permission_classes = [IsConsumidorAndOwner2]
    def get_object(self, instance):
        try:
            return DetalhesEnvio.objects.filter(consumidor=instance)
        except DetalhesEnvio.DoesNotExist:
            raise Http404

    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404
    def get(self, request, username, format=None):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        detalhes_envio_objetos = self.get_object(consumidor)
        if detalhes_envio_objetos.exists():
            serializar = DetalhesEnvioSerializerResponse(detalhes_envio_objetos, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)
    def post(self, request, username, format=None):
        utilizador = self.get_utilizador(username)
        data2 = request.data.copy()
        consumidor = self.get_consumidor(utilizador)
        data2['consumidor'] = consumidor.id
        
        if 'guardar_esta_morada' not in data2.keys():
            data2['guardar_esta_morada'] = False
        
        
        if 'usar_informacoes_utilizador' not in data2.keys():
            data2['usar_informacoes_utilizador'] = False
        
        nome_bool = True if data2.get('nome') is not None else False
        pais_bool = True if data2.get('pais') is not None else False
        cidade_bool = True if data2.get('cidade') is not None else False
        morada_bool = True if data2.get('morada') is not None else False
        telemovel_bool = True if data2.get('telemovel') is not None else False
        email_bool = True if data2.get('email') is not None else False
        if nome_bool and pais_bool and cidade_bool and morada_bool and telemovel_bool and email_bool: #enviou todos os campos obrigatórios
            if (data2['usar_informacoes_utilizador'] == 'True' or data2['usar_informacoes_utilizador']==True) and (utilizador.nome != data2.get('nome') or utilizador.pais != data2.get('pais') or utilizador.cidade != data2.get('cidade') or utilizador.telemovel != data2.get('telemovel') or utilizador.email != data2.get('email') or (data2.get('morada') != utilizador.morada and utilizador.morada is not None)):
                #escolheu usar informações do utilizador mas existe algum que não está igual
                erroString = "Escolheu usar as informações do utilizador, mas está campos diferentes aos que tem guardados. Os campos diferentes: "
                erroString+= "nome " if utilizador.nome != data2.get('nome') else ''
                erroString+= "pais " if utilizador.pais != data2.get('pais') else ''
                erroString+= "cidade " if utilizador.cidade != data2.get('cidade') else ''
                erroString+= "morada " if (data2.get('morada') != utilizador.morada and utilizador.morada is not None) else ''
                erroString+= "telemovel " if utilizador.telemovel != data2.get('telemovel') else ''
                erroString+= "email" if utilizador.email != data2.get('email') else ''
                erroString+= ". Altere estes campos para o valor que tem guardado."
                return Response({'details': erroString}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        if (data2['usar_informacoes_utilizador'] == 'True' or data2['usar_informacoes_utilizador'] == True): #escolheu usar informacoes do utilizador
            if (utilizador.nome == data2.get('nome') or utilizador.pais.name == data2.get('pais') or utilizador.cidade == data2.get('cidade')or utilizador.telemovel == data2.get('telemovel')or utilizador.email == data2.get('email') or (data2.get('morada') == utilizador.morada and utilizador.morada is not None)):
                pass #a informacao está toda igual?
            elif nome_bool==False and pais_bool == False and cidade_bool == False and morada_bool == False and telemovel_bool == False and email_bool == False:
                ###escolheu usar informação do utilizador e não enviou nenhum campo obrigatório
                data2['nome'] = utilizador.nome
                data2['pais'] = utilizador.pais
                data2['cidade'] = utilizador.cidade
                
                if utilizador.morada is not None:
                    data2['morada'] = utilizador.morada 
                elif utilizador.morada is None:
                    return Response({'morada':"Escolheu usar informações do utilizador. Mas ainda não tem a sua morada guardada. Envie a sua morada, e se pretender guardar, defina 'guardar_esta_morada' igual a true!"}, status=status.HTTP_400_BAD_REQUEST)           
                
                
                if True: #esconder esta lógica para facilitar leitura do código
                    ### campo telemovel
                    telemovel = utilizador.telemovel
                    ####converter telemovel para formato internacional
                    international_phone_number = phonenumbers.format_number(telemovel, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    ### converte para str
                    telemovel_international_str = str(international_phone_number)
                    #### atribui str ao dicionario, pq JSON  n suporta PhoneNumber
                data2['telemovel'] = telemovel_international_str
                data2['email'] = utilizador.email
        
        if (data2['usar_informacoes_utilizador'] == 'True' or data2['usar_informacoes_utilizador'] == True) and morada_bool:
            data2['nome'] = utilizador.nome
            data2['pais'] = utilizador.pais
            data2['cidade'] = utilizador.cidade
            if True: #esconder esta lógica para facilitar leitura do código
                ### campo telemovel
                telemovel = utilizador.telemovel
                ####converter telemovel para formato internacional
                international_phone_number = phonenumbers.format_number(telemovel, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                ### converte para str
                telemovel_international_str = str(international_phone_number)
                #### atribui str ao dicionario, pq JSON  n suporta PhoneNumber
            data2['telemovel'] = telemovel_international_str
            data2['email'] = utilizador.email
            morada = data2['morada']
            vazio = morada.replace(" ","")
            if vazio == '':
                return Response({'morada':"Morada inválida. Selecione uma morada que não seja uma string vazia"}, status=status.HTTP_400_BAD_REQUEST)
            
        guardar_esta_morada = data2.get('guardar_esta_morada')
        
        deserializer = DetalhesEnvioSerializerRequest(data=data2)
        if deserializer.is_valid():
            with transaction.atomic():
                if guardar_esta_morada==True:
                    utilizador.morada = data2['morada']  
                    utilizador.save()          
                deserializer.save()
                respostaSerializar = DetalhesEnvioSerializerResponse(deserializer.instance)
                return Response(respostaSerializar.data, status=status.HTTP_201_CREATED)
        print(deserializer.errors) 
        return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DetalhesEnvioDetails(APIView):
    permission_classes = [IsConsumidorAndOwner2]
    def get_object(self, instance, id):
        try:
            return DetalhesEnvio.objects.get(consumidor=instance, id=id)
        except DetalhesEnvio.DoesNotExist:
            raise Http404
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404
    def get(self, request, username, id):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        detalhesEnvio = self.get_object(consumidor, int(id))
        if detalhesEnvio is not None:
            serializar = DetalhesEnvioSerializerResponse(detalhesEnvio, many=False)
            return Response(serializar.data, status=status.HTTP_200_OK)
        elif detalhesEnvio is None:
            return Response(status.HTTP_404_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, username, id):
        utilizador = self.get_utilizador(username) #vai buscar o utlizador
        consumidor = self.get_consumidor(utilizador) # vai buscar consumidor
        detalhesEnvio = self.get_object(consumidor, int(id)) # vai buscar detalhes de envio
        if detalhesEnvio is None:
            return Response({'detail':f'Detalhes de envio do utilizador {username} com o id {id} não encontrados'}, status=status.HTTP_404_NOT_FOUND)
        
        data2 = request.data.copy() #copia o request.data para este poder ser alterado

##########################NOVO####################
        morada_detalhesEnvio = detalhesEnvio.morada # recebe a morada já guardada

        if 'guardar_esta_morada' not in data2.keys(): # se guardar_esta_morada não estiver no pedido
            data2['guardar_esta_morada'] = False #não é para guardar
        
        
        if 'usar_informacoes_utilizador' not in data2.keys(): # se usar_informacoes_utilizador não estiver no pedido
            data2['usar_informacoes_utilizador'] = False #não é para usar as informacoes do utilizador
        
        ##para verificações mais à frente
        nome_bool = True if data2.get('nome') is not None else False # foi enviado nome no pedido?
        pais_bool = True if data2.get('pais') is not None else False # foi enviado pais no pedido?
        cidade_bool = True if data2.get('cidade') is not None else False # foi enviado cidade no pedido?
        morada_bool = True if data2.get('morada') is not None else False # foi enviado morada no pedido?
        telemovel_bool = True if data2.get('telemovel') is not None else False # foi enviado telemovel no pedido?
        email_bool = True if data2.get('email') is not None else False # foi enviado email no pedido?
        # usar_informacoes utilizador é igual a true, e se algum dos outros campos tiver sido enviado
        if data2['usar_informacoes_utilizador'] == True and (
                                                            nome_bool == True or  
                                                            pais_bool == True or 
                                                            cidade_bool == True or 
                                                            (morada_bool == True or utilizador.morada is not None ) #foi enviada morada ou o utilizador tem alguma morada guardada?
                                                            or telemovel_bool == True or email_bool == True):
            if utilizador.nome == data2.get('nome') and utilizador.pais.name == data2.get('pais') and utilizador.cidade == data2.get('cidade') and utilizador.telemovel == data2.get('telemovel') and utilizador.email == data2.get('email') and (data2.get('morada') == utilizador.morada or utilizador.morada is None):
            #(lembrar que é para usar infos do utillizador) 
            # o nome enviado é igual ao nome do utilizador?
            # o nome do pais enviado é igual ao guardado no utilizador?
            # a cidade enviada é igual é igual à guardada no utilizador?
            # o telemóvel enviado é igual ao guardada no utilizador?
            # o email enviado é igual ao guardada no utilizador?
            # a morada enviada é igual à guardada no utilizador ou o utilizador não tem morada guardada?
                pass
            
            else:
                erroString = "Escolheu usar as informações do utilizador. \
                            Mas está a definir valores diferentes aos guardados na criação  da conta. \
                            Campos diferentes aos guardados na conta: "
                erroString+= "nome, " if utilizador.nome != data2.get('nome') else ''
                erroString+= "pais, " if utilizador.pais.name != data2.get('pais') else ''
                erroString+= "cidade, " if utilizador.cidade != data2.get('cidade') else ''
                erroString+= "morada, " if utilizador.morada != data2.get('morada') else ''
                erroString+= "telemovel, " if utilizador.telemovel != data2.get('telemovel')else ''
                erroString+= "email" if utilizador.email != data2.get('email') else ''
                erroString+= ". Remova estes campos ou coloque os valores guardados aquando a criação da conta."
                return Response({'details': erroString}, status=status.HTTP_400_BAD_REQUEST)
        
        # definiu usar informacoes do utilizador e não enviou nenhum campo respetivo do utilizador. definir valores guardados no utilizador
        if data2['usar_informacoes_utilizador'] == True and nome_bool==False and pais_bool==False and cidade_bool==False and morada_bool ==False and telemovel_bool== False  and email_bool == False:
            data2['nome'] = utilizador.nome
            data2['pais'] = utilizador.pais
            data2['cidade'] = utilizador.cidade
            if utilizador.morada is not None:
                data2['morada'] = utilizador.morada
            elif utilizador.morada is None and data2.get('morada') is None:
                if morada_detalhesEnvio == '' or morada_detalhesEnvio is None:
                    return Response({'morada':"Escolheu usar informações do utilizador. Mas ainda não tem a sua morada guardada. Envie a sua morada, e se pretender guardar, defina 'guardar_esta_morada' !"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data2['morada'] = morada_detalhesEnvio
            if True: #esconder esta lógica para facilitar leitura do código
                ### campo telemovel
                telemovel = utilizador.telemovel
                ####converter telemovel para formato internacional
                international_phone_number = phonenumbers.format_number(telemovel, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                ### converte para str
                telemovel_international_str = str(international_phone_number)
                #### atribui str ao dicionario, pq JSON  n suporta PhoneNumber
            data2['telemovel'] = telemovel_international_str
            data2['email'] = utilizador.email
        
        
        guardar_esta_morada = True if data2.get('guardar_esta_morada')=='True' else False
        data2['consumidor'] = consumidor.id #atribui o id do user logado ao campo consumidor 
        serializer = DetalhesEnvioSerializerRequest(detalhesEnvio, data=data2)
        if serializer.is_valid():
            with transaction.atomic():
                if guardar_esta_morada:
                    utilizador.morada = data2['morada']  
                    utilizador.save()          
                serializer.save()
                respostaSerializar = DetalhesEnvioSerializerResponse(serializer.instance)
                return Response(respostaSerializar.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, username, id):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        detalhesEnvio = self.get_object(consumidor, int(id))
        if detalhesEnvio is None:
            return Response({'detail':f'Detalhes de envio do utilizador {username} com o id {id} não encontrados'}, status=status.HTTP_404_NOT_FOUND)
        detalhesEnvio.delete()
        return Response({"details":"No content! Apagado com sucesso!"},status=status.HTTP_204_NO_CONTENT)

class EncomendaList(APIView):
    permission_classes = [IsConsumidorAndOwner2]
    #permission_classes = [IsAuthenticated]
    def get_DetalhesEnvio(self, instance, pk):
        try:
            return DetalhesEnvio.objects.filter(consumidor=instance,id=pk)
        except DetalhesEnvio.DoesNotExist:
            raise Http404

    def get_object(self, instance):
        try:
            return Encomenda.objects.filter(consumidor=instance)
        except Encomenda.DoesNotExist:
            raise Http404
        

    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404

    def getCarrinho(self,consumidor):
        try:
            return Carrinho.objects.get(consumidor=consumidor)
        except Carrinho.DoesNotExist:
            raise Http404

    def getProdutosCarrinho(self,carrinho):
        try:
            return ProdutosCarrinho.objects.filter(carrinho=carrinho)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404
          
    def get(self, request, username, format=None):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        encomenda_objetos = self.get_object(consumidor)
        if encomenda_objetos is not None:
            serializar = EncomendaSerializer(encomenda_objetos, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)


    def post(self, request, username, format=None):
        utilizador = self.get_utilizador(username)
        data2 = request.data.copy()

            
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)

        carrinho=self.getCarrinho(consumidor)
        produtosCarrinho=self.getProdutosCarrinho(carrinho)

        total=0
        for produto in produtosCarrinho:
            total+=produto.preco

        data2["consumidor"]=consumidor.id
        data2["valor_total"]=total

        deserializer = EncomendaSerializer(data=data2)

        if deserializer.is_valid():
           
            deserializer.save()
            return Response(deserializer.data, status=status.HTTP_201_CREATED)
        print(deserializer.errors)
        return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EncomendaDetail(APIView):
    permission_classes = [IsConsumidorAndOwner2]
    def get_DetalhesEnvio(self, instance):
        try:
            return DetalhesEnvio.objects.filter(consumidor=instance)
        except DetalhesEnvio.DoesNotExist:
            raise Http404

    def get_object(self, consumidor, instance):
        try:
            return Encomenda.objects.get(id=instance, consumidor=consumidor)
        except Encomenda.DoesNotExist:
            raise Http404
        
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404

    def getCarrinho(self,consumidor):
        try:
            return Carrinho.objects.get(consumidor=consumidor)
        except Carrinho.DoesNotExist:
            raise Http404

    def getProdutosCarrinho(self,carrinho):
        try:
            return ProdutosCarrinho.objects.get(carrinho=carrinho)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404
          
    def get(self, request, username, idEncomenda, format=None):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        encomenda_objetos = self.get_object(consumidor,idEncomenda)
        print(type(encomenda_objetos))
        if encomenda_objetos is not None:
            serializar = EncomendaSerializer(encomenda_objetos, many=False)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)

    def put(self, request, username, idEncomenda, format=None):
        data2=request.data.copy()
        
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        encomenda_objetos = self.get_object(consumidor,idEncomenda)

        if encomenda_objetos is not None:
            data2["consumidor"]=consumidor.id
            deserializer=EncomendaSerializer(encomenda_objetos, data=data2)
            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_200_OK)
            return Response(deserializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, username,idEncomenda, format=None):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        encomenda_objetos = self.get_object(consumidor,idEncomenda)

        if encomenda_objetos.exists():
            encomenda_objetos.delete()
            return Response(f"Encomenda do consumidor '{consumidor}' apagada com sucesso!",status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)





class ProdutosEncomendaList(APIView):
    #permission_classes = [IsConsumidorAndOwner2]

    def get_object(self, instance):
        try:
            return ProdutosEncomenda.objects.filter(encomenda=instance)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
        
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404

    def getCarrinho(self,consumidor):
        try:
            return Carrinho.objects.get(consumidor=consumidor)
        except Carrinho.DoesNotExist:
            raise Http404

    def getProdutosCarrinho(self,carrinho):
        try:
            return ProdutosCarrinho.objects.get(carrinho=carrinho)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404
          
    def get(self, request, username,idEncomenda, format=None):

        produtos_encomenda_objetos = self.get_object(idEncomenda)
        if produtos_encomenda_objetos.exists():
            serializar = ProdutosEncomendaSerializer(produtos_encomenda_objetos, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)


    def getProdutoUP(self, idProduto):
        try:
            return ProdutoUnidadeProducao.objects.get(id=idProduto)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404

    def post(self, request, username, idEncomenda, format=None):

        data2 = request.data.copy()

        data2["encomenda"]=idEncomenda
        idProdutoUP=data2["produtos"]

        produto=self.getProdutoUP(idProdutoUP)
        if produto is not None:
            unidadeProducao=produto.unidade_producao
            precoKilo=produto.preco_a_granel if produto.preco_a_granel is not None else produto.preco_por_unidade
            quantidade=data2["quantidade"]
            preco=precoKilo*quantidade
            data2["unidadeProducao"]=unidadeProducao.id
            data2["precoKilo"]=precoKilo
            data2["preco"]=preco

            deserializer = ProdutosEncomendaSerializer(data=data2)

            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_201_CREATED)
            print(deserializer.errors)
            return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"details":"Produto não encontrado"},status=status.HTTP_404_NOT_FOUND)
    

class ProdutosEncomendaDetail(APIView):
    permission_classes = [IsConsumidorAndOwner2]

    def get_object(self, instance):
        try:
            return ProdutosEncomenda.objects.get(id=instance)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
        
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404

    def getCarrinho(self,consumidor):
        try:
            return Carrinho.objects.get(consumidor=consumidor)
        except Carrinho.DoesNotExist:
            raise Http404

    def getProdutosCarrinho(self,carrinho):
        try:
            return ProdutosCarrinho.objects.get(carrinho=carrinho)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404
          
    def get(self, request, username,idEncomenda,idProdutoEncomenda, format=None):

        produtos_encomenda_objetos = self.get_object(idProdutoEncomenda)
        if produtos_encomenda_objetos is not None:
            serializar = ProdutosEncomendaSerializer(produtos_encomenda_objetos, many=False)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)

    def getProdutoUP(self, idProduto):
        try:
            return ProdutoUnidadeProducao.objects.get(id=idProduto)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404
        
    def put(self, request, username, idEncomenda,idProdutoEncomenda, format=None):

        produts_encomenda_objetos = self.get_object(idProdutoEncomenda)

        if produts_encomenda_objetos.exists():

            deserializer=EncomendaSerializer(produts_encomenda_objetos, data=request.data)
            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_200_OK)
            return Response(deserializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, username,idEncomenda,idProdutoEncomenda, format=None):

        produts_encomenda_objetos = self.get_object(idProdutoEncomenda)

        if produts_encomenda_objetos.exists():
            idProdutoUP=produts_encomenda_objetos.id
            produtoUP=self.getProdutoUP(idProdutoUP)
            produts_encomenda_objetos.delete()
            return Response(f"{produtoUP}' encomendado, cancelado com sucesso!",status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)





class ProdutoEncomendasCancelarView(APIView):
    """_summary_\

    Args:
        APIView (_type_): _description_

    Raises:
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_
        Http404: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = [IsConsumidorAndOwner2]
    def get_object(self, instance):
        try:
            return ProdutosEncomenda.objects.get(id=instance)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
        
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    
    def get_consumidor(self, utilizador):
        try:
            return Consumidor.objects.get(utilizador=utilizador)
        except Consumidor.DoesNotExist:
            raise Http404

    def getCarrinho(self,consumidor):
        try:
            return Carrinho.objects.get(consumidor=consumidor)
        except Carrinho.DoesNotExist:
            raise Http404

    def getProdutosCarrinho(self,carrinho):
        try:
            return ProdutosCarrinho.objects.get(carrinho=carrinho)
        except ProdutosCarrinho.DoesNotExist:
            raise Http404
    
    def getProdutoUP(self, idProduto):
        try:
            return ProdutoUnidadeProducao.objects.get(id=idProduto)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404
    
    
    def get(self, request, username,idEncomenda,idProdutoEncomenda, format=None):

        produtos_encomenda_objetos = self.get_object(idProdutoEncomenda)
        if produtos_encomenda_objetos is not None:
            serializar = ProdutosEncomendaSerializer(produtos_encomenda_objetos, many=False)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)
    
    def put(self, request, username, idEncomenda, idProdutoEncomenda, format=None):
        produtos_encomenda_objetos = self.get_object(idProdutoEncomenda)
        if produtos_encomenda_objetos is not None:
            idProdutoUP=produtos_encomenda_objetos.produtos.id
            produtoUP = produtos_encomenda_objetos.produtos
            if produtos_encomenda_objetos.estado == 'Em processamento':
                prazo_cancelamento = timedelta(hours=3) ##### quanto tempo dar para se cancelar?
                tempo_decorrido_desde_encomenda = timezone.now() - produtos_encomenda_objetos.created
                if tempo_decorrido_desde_encomenda < prazo_cancelamento:
                    produtos_encomenda_objetos.estado = 'Cancelado'
                    produtos_encomenda_objetos.save()
                    return Response(f"{produtoUP}' encomendado, cancelado com sucesso!",status=status.HTTP_200_OK)
                else:
                    return Response({"details":"Erro - Periodo para cancelamento de encomenda expirado! Tempo máximo de 3h para cancelar encomendas!" }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"details":"Erro- Já não pode cancelar a encomenda. Já não está no estado 'Em processamento'"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)





class EncomendarTodosOsProdutosCarrinho(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    permission_classes = [IsConsumidorAndOwner2, IsAuthenticated]
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_consumidor(self, instance):
        try:
            return Consumidor.objects.get(utilizador=instance)
        except Consumidor.DoesNotExist:
            raise Http404
    def get_carrinho(self, instance):
        try:
            return Carrinho.objects.get(consumidor=instance)
        except Carrinho.DoesNotExist:
            raise Http404
    def get_produtos_carrinho(self, instance):
        try:
            return ProdutosCarrinho.objects.filter(carrinho=instance)            
        except ProdutosCarrinho.DoesNotExist:
            raise Http404
    def get_detalhes_envio(self, instance, idDetalhesEnvio):
        try:
            return DetalhesEnvio.objects.get(consumidor=instance, id=idDetalhesEnvio)
        except DetalhesEnvio.DoesNotExist:
            raise Http404
    def get_encomendas(self, consumidor):
        try:
            return Encomenda.objects.filter(consumidor=consumidor)
        except Encomenda.DoesNotExist:
            raise Http404
    def get_produtos_up(self,id):
        try:
            return ProdutoUnidadeProducao.objects.get(id=id)
        except ProdutoUnidadeProducao.DoesNotExist:
            raise Http404
    
    def get(self, request, username, format=None):
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        encomendas = self.get_encomendas(consumidor)
        if encomendas is not None:
            serializar = EncomendaSerializer(encomendas, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)
            
    def post(self, request, username, format=None):
        data2 = request.data.copy()
        utilizador = self.get_utilizador(username)
        consumidor = self.get_consumidor(utilizador)
        carrinho = self.get_carrinho(consumidor)
        produtos_carrinho = self.get_produtos_carrinho(carrinho)
        total = 0
        produtos_sem_stock = []
        print("ANTES DO ATOMIC!!!!!!!!!!!!!!!!!")
        with transaction.atomic():
            if produtos_carrinho is not None:
                print("EXISTEM PRODUTOS NO CARRINHO!!!!")
                for itemCarrinho in produtos_carrinho:
                    idProdutoUP = itemCarrinho.produto.id
                    quantidade = itemCarrinho.quantidade
                    total += itemCarrinho.preco
                    produto_up = self.get_produtos_up(idProdutoUP)
                    stock_produtos_up = produto_up.stock
                    if stock_produtos_up < quantidade:
                        produtos_sem_stock.append((produto_up, itemCarrinho.id))
                if produtos_sem_stock != []:
                    print("EXISTEM PRODUTOS sem stock!!!!")
                    stringBuilder = ''
                    for par in produtos_sem_stock:
                        stringBuilder += "ERRO: O " + str(par[0]) + " com o id no carrinho " + str(
                            par[1]) + " não tem stock para a quantidade pretendida. O stock disponível é " + str(
                            par[0].stock) + ".\n"
                    return Response({"details": stringBuilder}, status=status.HTTP_404_NOT_FOUND)

                id_detalhes_envio = data2['detalhes_envio']
                detalhes_envio = self.get_detalhes_envio(consumidor, id_detalhes_envio)
                if detalhes_envio is not None:
                    print("EXISTEM DETALHES ENVIO!!!!")
                    encomenda = Encomenda.objects.create(
                        consumidor=consumidor,
                        detalhes_envio=detalhes_envio,
                        valor_total=total
                    )
                    encomenda.save()
                    for itemCarrinho in produtos_carrinho:
                        idProdutoUP = itemCarrinho.produto.id
                        quantidade_temp = itemCarrinho.quantidade
                        produto_up = self.get_produtos_up(idProdutoUP)
                        stock_produtos_up = produto_up.stock
                        if stock_produtos_up >= quantidade_temp:
                            print("STOCK OKKKK!!!!")
                            stock_produtos_up -= quantidade_temp
                            produto_up.stock = stock_produtos_up
                            produto_up.save()
                        produto_encomenda = ProdutosEncomenda.objects.create(
                            encomenda=encomenda,
                            produtos=produto_up,
                            unidadeProducao=produto_up.unidade_producao,
                            quantidade=quantidade_temp,
                            preco=itemCarrinho.preco,
                            precoKilo=itemCarrinho.precoKilo
                        )
                        itemCarrinho.delete()
                        produto_encomenda.save()

                    serializar = EncomendaSerializer(encomenda, many=False)
                    return Response(serializar.data, status=status.HTTP_201_CREATED)
                else:
                    print("PRIMEIRO ELSEEEE!!!")
                    return Response({"details": "Não enviou os detalhes de envio ou os detalhes de envio selecionados não lhe pertencem"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                print("SEGUNDO ELSEEEE!!!")
                return Response({'details': "Não tem produtos no carrinho"})
        return Response({"details": "Ocorreu um erro ao processar a encomenda. Todas as alterações foram revertidas."},status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    
class EncomendasPorUPList(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    permission_classes = [IsFornecedorAndOwner2]
    def get_object(self, instance):
        try:
            return ProdutosEncomenda.objects.filter(unidadeProducao =instance)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
        
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_fornecedor(self, utilizador):
        try:
            return Fornecedor.objects.get(utilizador=utilizador)
        except Fornecedor.DoesNotExist:
            raise Http404

    def get_up(self, fornecedor, idUP):
        try:
            return UnidadeProducao.objects.get(id=idUP, fornecedor=fornecedor)
        except UnidadeProducao.DoesNotExist:
            raise Http404
          
    def get(self, request, username,idUnidadeProducao, format=None):
        user = self.get_utilizador(username)
        fornecedor = self.get_fornecedor(user)
        up = self.get_up(fornecedor, idUnidadeProducao)
        produtos_encomenda_objetos = self.get_object(up)
        if produtos_encomenda_objetos.exists():
            serializar = ProdutosEncomendaSerializer(produtos_encomenda_objetos, many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)
    
class EncomendasPorUPDetail(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    permission_classes = [IsFornecedorAndOwner2]
    def get_object(self, instance, idEncomenda):
        try:
            return ProdutosEncomenda.objects.filter(unidadeProducao =instance, id=idEncomenda)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
        
    def get_utilizador(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_fornecedor(self, utilizador):
        try:
            return Fornecedor.objects.get(utilizador=utilizador)
        except Fornecedor.DoesNotExist:
            raise Http404

    def get_up(self, fornecedor, idUP):
        try:
            return UnidadeProducao.objects.get(id=idUP, fornecedor=fornecedor)
        except UnidadeProducao.DoesNotExist:
            raise Http404
          
    def get(self, request, username,idUnidadeProducao,idEncomenda, format=None):
        user = self.get_utilizador(username)
        fornecedor = self.get_fornecedor(user)
        up = self.get_up(fornecedor, idUnidadeProducao)
        produtos_encomenda_objetos = self.get_object(up, idEncomenda)
        if produtos_encomenda_objetos.exists():
            serializar = ProdutosEncomendaSerializer(produtos_encomenda_objetos, many=False)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)
    
    
    
    
class getDetalhesParaForncedorDetails(APIView):
    """
    Fornecedor receber detalhes de envio de uma encomenda
    Args:
        APIView (_type_): _description_
    """
    def get_object(self, id):
        try:
            return DetalhesEnvio.objects.get(id=id)
        except DetalhesEnvio.DoesNotExist:
            raise Http404
    def get_encomenda(self, id):
        try:
            return Encomenda.objects.get(id=id)
        except Encomenda.DoesNotExist:
            raise Http404
    def get(self, request, username, idEncomenda):
        encomenda = self.get_encomenda(idEncomenda)
        idDetalhesEnvio = encomenda.detalhes_envio.id
        detalhes_envio = self.get_object(idDetalhesEnvio)
        if detalhes_envio is not None:
            serializar = DetalhesEnvioSerializerResponse(detalhes_envio, many=False)
            return Response(serializar.data, status=status.HTTP_200_OK)
        return Response({"details":"Encomenda não encontrada"},status=status.HTTP_404_NOT_FOUND)
    
    
    
    
class ProdutosEncomendadosVeiculosList(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    permisson_classes = [IsFornecedorAndOwner2]
    def get_object(self, instance):
        try:
            return ProdutosEncomendadosVeiculos.objects.filter(veiculo=instance)
        except ProdutosEncomendadosVeiculos.DoesNotExist:
            raise Http404
    def get_veiculo(self, idVeiculo):
        try:
            return Veiculo.objects.get(id=idVeiculo)
        except Veiculo.DoesNotExist:
            raise Http404
    def get_unidade_producao(self, idUP, instance):
        try:
            return UnidadeProducao.objects.get(id=idUP, fornecedor=instance)
        except UnidadeProducao.DoesNotExist:
            raise Http404
        
    def get_user(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_produto_encomendado(self, idProdutoEncomendado):
        try:
            return ProdutosEncomenda.objects.get(id=idProdutoEncomendado)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
    def get(self, request, username, idUnidadeProducao, idVeiculo, format=None):
        """
        Listar todos os produtos encomendados associados a um dado veículo

        Args:
            request (): request do django
            username (str): username do link
            idUnidadeProducao (int): id da unidade de produção onde existe o produto encomendado e o veículo
            idVeiculo (_type_): id do veículo que está carregado com o produto encomendado
        Returns:
            json list: Par produto encomendado e veiculo que o carrega
        """
        veiculo = self.get_veiculo(idVeiculo)
        produtos_encomendados_por_veiculo = self.get_object(veiculo)
        if produtos_encomendados_por_veiculo is not None:
            serializar = ProdutosEncomendadosVeiculosSerializer(produtos_encomendados_por_veiculo, many=True)
            return Response(serializar.data, status=status.HTTP_200_OK)
        return Response({"details":"Produtos neste veiculo não foram encontrado"}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, username, idUnidadeProducao, idVeiculo, format=None):
        """Colocar produtos encomendados em veiculo de transporte

        Args:
            request (_type_): _description_
            username (_type_): _description_
            idUnidadeProducao (_type_): _description_
            idVeiculo (_type_): _description_
            format (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        data2 = request.data.copy()
        
        utilizador = self.get_user(username)
        fornecedor = utilizador.fornecedor
        up = self.get_unidade_producao(idUnidadeProducao, fornecedor)
        veiculo = self.get_veiculo(idVeiculo)
        if 'produto_Encomendado' not in data2:
            return Response({"details":f'Produto encomendado a ser colocado no veiculo não enviado. Enviar id do produto encomendado a ser colocado no veículo {veiculo} da unidade de produção:{up}. Use a chave "produto_Encomendado"'})
        if 'veiculo' not in data2:
            data2['veiculo'] = veiculo.id
        if 'veiculo' in data2 and data2.get('veiculo') != veiculo.id:
            return Response({"details":f"O veículo enviado tem de ser o mesmo que o veiculo está a ser escolhido no url"})
        idProdutoEncomendado = data2['produto_Encomendado']
        produto_encomendado = self.get_produto_encomendado(idProdutoEncomendado)
        if up.fornecedor.utilizador != request.user:
            return Response({"details":"Não tem autorização para realizar esta ação!"}, status=status.HTTP_403_FORBIDDEN)
        if produto_encomendado.unidadeProducao != veiculo.unidadeProducao:
            return Response({"details":"O produto encomendado tem de ser colocado num veículo da unidade de produção onde o produto foi encomendado!"}, status=status.HTTP_400_BAD_REQUEST)
        if produto_encomendado.estado == 'Enviado' or produto_encomendado == 'A chegar' or produto_encomendado.estado == 'Entregue' or produto_encomendado.estado == 'Cancelado':
            return Response({"details":f"Não pode realizar esta ação. O produto já se encontra no estado {produto_encomendado.estado}"}, status=status.HTTP_400_BAD_REQUEST)
        if veiculo.estado_veiculo != 'D' and veiculo.estado_veiculo !='C':
            return Response({"details":f"Não pode adicionar produtos encomendados a um veículo que não esteja disponível. Estado do veículo {veiculo.estado_veiculo}"}, status=status.HTTP_400_BAD_REQUEST)
        data2['veiculo'] =  veiculo.id
        with transaction.atomic():
            serializar = ProdutosEncomendadosVeiculosSerializer(data=data2)
            if serializar.is_valid():
                serializar.save()
                veiculo.estado_veiculo = 'C'
                veiculo.save()
                return Response(serializar.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializar.errors, status=status.HTTP_400_BAD_REQUEST)



class ProdutosEncomendadosVeiculosPorProduto(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    permisson_classes = [IsFornecedorAndOwner2]
    def get_object(self, instance):
        try:
            return ProdutosEncomendadosVeiculos.objects.filter(produto_Encomendado=instance)
        except ProdutosEncomendadosVeiculos.DoesNotExist:
            raise Http404        
    def get_user(self, username):
        try:
            return Utilizador.objects.get(username=username)
        except Utilizador.DoesNotExist:
            raise Http404
    def get_produto_encomendado(self, idProdutoEncomendado, idUnidadeProducao):
        try:
            return ProdutosEncomenda.objects.get(id=idProdutoEncomendado, unidadeProducao=idUnidadeProducao)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
    def get(self, request, username, idProdutoEncomendado, idUnidadeProducao,format=None):
        """
        Listar todos os produtos encomendados associados a um dado veículo, por id de produto encomendado

        Args:
            request (): request do django
            username (str): username do link
            idUnidadeProducao (int): id da unidade de produção onde existe o produto encomendado e o veículo
            idVeiculo (_type_): id do veículo que está carregado com o produto encomendado
        Returns:
            json list: Par produto encomendado e veiculo que o carrega
        """
        produtoEncomendado = self.get_produto_encomendado(idProdutoEncomendado, idUnidadeProducao)
        produtos_encomendados_por_veiculo = self.get_object(produtoEncomendado)
        if produtos_encomendados_por_veiculo.exists():
            serializar = ProdutosEncomendadosVeiculosSerializer(produtos_encomendados_por_veiculo, many=True)
            return Response(serializar.data, status=status.HTTP_200_OK)
        return Response({"details":"Este produto não está em nenhum veiculo"}, status=status.HTTP_404_NOT_FOUND)






class VeiculoSaida(APIView):
    """
    Colocar um veiculo de saida da UP
    """
    def get_object(self, instancia):
        try:
            return ProdutosEncomendadosVeiculos.objects.filter(veiculo=instancia)
        except ProdutosEncomendadosVeiculos.DoesNotExist:
            raise Http404
    def get_veiculo(self, idVeiculo, instancia):
        try:
            return Veiculo.objects.get(id=idVeiculo, unidadeProducao=instancia)
        except Veiculo.DoesNotExist:
            raise Http404
    def get_up(self, idUP):
        try:
            return UnidadeProducao.objects.get(id=idUP)
        except UnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request, username,idUnidadeProducao, idVeiculo ,format=None):
        uni_producao = self.get_up(idUnidadeProducao)
        veiculo = self.get_veiculo(idVeiculo, uni_producao)
        if veiculo is not None:
            produtos_encomendados_veiculo = self.get_object(veiculo)
            if produtos_encomendados_veiculo is not None:
                serializar = ProdutosEncomendadosVeiculosSerializer(produtos_encomendados_veiculo, many=True)
                return Response(serializar.data, status=status.HTTP_200_OK)            
            else:
                return Response({"details":"Este veículo não tem produtos encomendados carregados!"},status=status.HTTP_404_NOT_FOUND)
    def get_produto_encomendado(self, id):
        try:
            return ProdutosEncomenda.objects.get(id=id)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404        
    
    def put(self, request, username, idUnidadeProducao, idVeiculo, format=None):
        uni_producao = self.get_up(idUnidadeProducao)
        veiculo = self.get_veiculo(idVeiculo, uni_producao)
        produtos_encomendados_objeto = veiculo.produtos_no_veiculo.all()
        print(produtos_encomendados_objeto)
        print(len(produtos_encomendados_objeto))
        if veiculo is not None and len(produtos_encomendados_objeto)!=0:
            print("ENTREI NO 1º IF")
            if veiculo.estado_veiculo == 'C':
                with transaction.atomic():
                    veiculo.estado_veiculo = "E"
                    veiculo.save()

                    # print(produtos_encomendados_objeto)
                    # print(type(produtos_encomendados_objeto[0]))
                    primeiro_produto_encomendado_carregado_no_carrinho = produtos_encomendados_objeto.first()
                    if primeiro_produto_encomendado_carregado_no_carrinho:
                        idProdutoEncomendado = primeiro_produto_encomendado_carregado_no_carrinho.produto_Encomendado.id
                        produtoEncomendado = self.get_produto_encomendado(idProdutoEncomendado)
                        produtoEncomendado.estado = 'A chegar'
                        # produtoEncomendado = primeiro_produto_encomendado_carregado_no_carrinho.produto_Encomendado.estado = 'A chegar'
                        produtoEncomendado.save()
                        for produto_carregado in produtos_encomendados_objeto[1:]:
                            idProdutoEncomendado = produto_carregado.produto_Encomendado.id
                            produtoEncomendado = self.get_produto_encomendado(idProdutoEncomendado)
                            produtoEncomendado.estado = 'Enviado'
                        # produtoEncomendado = primeiro_produto_encomendado_carregado_no_carrinho.produto_Encomendado.estado = 'A chegar'
                            produtoEncomendado.save()
                        produtos_encomendados_veiculo = self.get_object(veiculo)
                        serializar = ProdutosEncomendadosVeiculosSerializer(produtos_encomendados_veiculo, many=True)
                        return Response(serializar.data, status=status.HTTP_200_OK) 
                    else:
                        return Response({"details":"Veículo  sem produtos carregados"}, stauts=status.HTTP_404_NOT_FOUND)
                    
            else:
                return Response({"details":f"Não pode realizar esta ação! O veículo não está no estado a carregar. Está no estado {veiculo.estado_veiculo}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("ENTREI NESTE ELSE")
            return Response({"details":"Veículo não encotrado, ou veículo sem produtos carregados"}, stauts=status.HTTP_404_NOT_FOUND)
        
        
        
        
        
class VeiculosDisponiveisParaCarregar(APIView):
    permisson_classes = [IsFornecedorAndOwner2]
    def get_object(self, instanciaUP):
        try:
            return Veiculo.objects.filter(
            Q(unidadeProducao=instanciaUP) &
            (
                Q(estado_veiculo='D') | Q(estado_veiculo="C")
            )
            )
        except Veiculo.DoesNotExist:
            raise Http404
    def get_up(self, idUP):
        try:
            return UnidadeProducao.objects.get(id=idUP)
        except UnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request,username, idUnidadeProducao):
        instanciaUP = self.get_up(idUnidadeProducao)
        veiculos = self.get_object(instanciaUP)
        if veiculos.exists():
            serializar = VeiculoSerializer(veiculos, many=True)
            return Response(serializar.data, status=status.HTTP_200_OK)
        return Response({"details":f"Veiculos disponiveis para serem carregados na UP:{instanciaUP}, não foram encontrados"}, status=status.HTTP_404_NOT_FOUND)
    


class FazerEntrega(APIView):
    """
    """
    permission_classes = [IsFornecedorAndOwner2]
    def get_object(self, instanciaVeiculo):
        try:
            return ProdutosEncomendadosVeiculos.objects.filter(veiculo=instanciaVeiculo)
        except ProdutosEncomendadosVeiculos.DoesNotExist:
            raise Http404
    def get_veiculo(self, idVeiculo, instanciaUP):
        try:
            return Veiculo.objects.get(id=idVeiculo, unidadeProducao=instanciaUP)
        except Veiculo.DoesNotExist:
            raise Http404
    def get_up(self, idUP):
        try:
            return UnidadeProducao.objects.get(id=idUP)
        except:
            raise Http404
    
    def get_produto_encomendado(self, idProdutoEncomendado):
        try:
            return ProdutosEncomenda.objects.get(id=idProdutoEncomendado)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
    def get_produtosEncomenda_por_Encomenda(self, instanciaEncomenda):
        try:
            return ProdutosEncomenda.objects.filter(encomenda=instanciaEncomenda)
        except ProdutosEncomenda.DoesNotExist:
            raise Http404
    def get_encomenda(self, idEncomenda):
        try:
            return Encomenda.objects.get(id=idEncomenda)
        except Encomenda.DoesNotExist:
            raise Http404
    
    
    def get(self, request, username, idUnidadeProducao, idVeiculo, format=None):
        up = self.get_up(idUnidadeProducao)
        veiculo = self.get_veiculo(idVeiculo, up)
        produtosEncomendadosVeiculo = self.get_object(veiculo)
        if produtosEncomendadosVeiculo.exists():
            primeiro_da_lista = produtosEncomendadosVeiculo.first()
            serializar = ProdutosEncomendadosVeiculosSerializer(primeiro_da_lista, many=False)
            return Response(serializar.data, status=status.HTTP_200_OK)
        return Response({"details":"Este veículo não tem produtos carregados para serem entregues."})
    def put(self, request, username, idUnidadeProducao, idVeiculo, format=None):
        up = self.get_up(idUnidadeProducao)
        veiculo = self.get_veiculo(idVeiculo, up)
        produtosEncomendadosVeiculo = self.get_object(veiculo)      
        data2 = request.data.copy()
        if produtosEncomendadosVeiculo.exists():
            with transaction.atomic():
                primeiro_da_lista = produtosEncomendadosVeiculo.first()
                produtoEncomendo = primeiro_da_lista.produto_Encomendado
                print("PRIMEIRO PRODUTO A SER ENTREGUE:",primeiro_da_lista)
                print("TIPO DO PRIMEIRO PRODUTO  A SER ENTREGUE:",type(primeiro_da_lista))
                #produtoEncomenda = self.get_produto_encomendado(idProdutoEncomenda)
                produtoEncomendo.estado = 'Entregue'
                produtoEncomendo.save()
                primeiro_da_lista.delete()                
                novos_produtosEncomendaVeiculo = self.get_object(veiculo)
                produtoEncomendo_2 = None
                if novos_produtosEncomendaVeiculo.exists():
                    print("PRODUTOS CARREGADOS NO CARRO:",novos_produtosEncomendaVeiculo)
                    novo_primeiro_da_lista = novos_produtosEncomendaVeiculo.first()
                    print("NOVO PRIMEIRO DA LISTA:", novo_primeiro_da_lista)
                    produtoEncomendo_2 = novo_primeiro_da_lista.produto_Encomendado
                    #novo_produto_encomendado = self.get_produto_encomendado(idProdutoEncomenda)
                    produtoEncomendo_2.estado = "A chegar"
                    produtoEncomendo_2.save()
                    print("PRODUTO ENCOMENDADO 2:", produtoEncomendo_2)
                    print("TIPO PRODUTO ENCOMENDADO:", type(produtoEncomendo_2))
                else:
                    veiculo.estado_veiculo = 'R'
                    veiculo.save()

                if produtoEncomendo is not None:
                    print("entrei!!!!")
                    print("produtoEncomendo", produtoEncomendo)
                    encomendaGeral = produtoEncomendo.encomenda
                    print(encomendaGeral, type(encomendaGeral))
                    produtos_da_encomenda_geral = self.get_produtosEncomenda_por_Encomenda(encomendaGeral)
                    quantosProdutosFinalizados = 0
                    for produto in produtos_da_encomenda_geral:
                        print("PRODUTO DA ENCOMENDA GERAK:", produto)
                        if produto.estado == 'Entregue':
                            quantosProdutosFinalizados+=1
                    if len(produtos_da_encomenda_geral) == quantosProdutosFinalizados:
                        print("Encomenda antes de alterar o estado", encomendaGeral)
                        encomendaGeral.estado = 'Entregue'
                        encomendaGeral.save()
                        print("Encomenda depois de alterar o estado", encomendaGeral)

                
                
            if novos_produtosEncomendaVeiculo.exists():
                serializar = ProdutosEncomendadosVeiculosSerializer(novos_produtosEncomendaVeiculo, many=True)
                return Response(serializar.data,status=status.HTTP_200_OK)
            else:
                serializar = VeiculoSerializer(veiculo, many=False)
                return Response(serializar.data,status=status.HTTP_200_OK)
        else:
            return Response({"details":"Não foram encontrados produtos para entregar neste veiculo"},status.HTTP_404_NOT_FOUND)

class VeiculoRegressou(APIView):
    """
    Veiculo regressa à up

    Args:
        APIView (_type_): _description_
    """
    permission_classes = [IsFornecedorAndOwner2]
    def get_object(self, instanciaUP, idVeiculo):
        try:
            return Veiculo.objects.get(unidadeProducao=instanciaUP, id=idVeiculo)
        except Veiculo.DoesNotExist:
            raise Http404
    def get_unidadeProducao(self, idUP):
        try:
            return UnidadeProducao.objects.get(id=idUP)
        except UnidadeProducao.DoesNotExist:
            raise Http404
    def get(self, request, username,idUnidadeProducao,idVeiculo):
        unidadeProducao = self.get_unidadeProducao(idUnidadeProducao)
        veiculo = self.get_object(unidadeProducao, idVeiculo)
        if veiculo is not None:
            serializar = VeiculoSerializer(veiculo, many=False)
            return Response(serializar.data, status=status.HTTP_200_OK)
        else:
            return Response({"details":"Veiculo não encontrado."}, stauts=status.HTTP_404_NOT_FOUND)
    def put(self, request, username,idUnidadeProducao, idVeiculo):
        unidadeProducao = self.get_unidadeProducao(idUnidadeProducao)
        veiculo = self.get_object(unidadeProducao, idVeiculo)
        if veiculo is not None:
            if veiculo.estado_veiculo == 'R':
                veiculo.estado_veiculo = 'D'
                veiculo.save()
                serializar = VeiculoSerializer(veiculo, many=False)
                respostaRegresso = {
                    "message": f"O veículo {veiculo} regressou com sucesso à unidade de produção {unidadeProducao}",
                    "data":serializar.data
                }
                
                return Response(respostaRegresso, status=status.HTTP_200_OK)
            else:
                respostaErro = {
                    "message": f"O veículo não se encontra no estado de Regresso. Encontra-se no estado: {veiculo.get_estado_veiculo_display()}"
                }
                return Response(respostaErro,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"details":"Veiculo não encontrado."}, stauts=status.HTTP_404_NOT_FOUND)




class RelatoiroImpactoLocalAdmin(APIView):
    def get_object(self):
        try:
            return Encomenda.objects.all()
        except Encomenda.DoesNotExist:
            raise Http404
    def get(self, request, username, format=None):
        if not request.user.is_authenticated:
            return Response({"details":"Não autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response({"detaisl":"Não autorizado"}, status=status.HTTP_403_FORBIDDEN)
        dinheiroGastoNoSite = 0
        encomendas = self.get_object()
        for encomenda in encomendas:
            dinheiroGastoNoSite+= encomenda.valor_total
            consumidor = encomenda.consumidor.utilizador # vai buscar o utilizador que é consumidor nesta encomenda
            
        
        
        print("UTILIZADOR:", repr(consumidor))
        print("DINHEIRO GASTO NO SITE: "+str(dinheiroGastoNoSite)+"€")
        serializar = EncomendaSerializer(encomendas, many=True)
        return Response(serializar.data, status=status.HTTP_200_OK)
        