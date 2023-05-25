### APP loja #####
### models.py ###
from loja.models import Utilizador, Consumidor, Fornecedor, UnidadeProducao, Veiculo, Categoria, Produto, Carrinho, ProdutoUnidadeProducao, ProdutosCarrinho
from .utilidades_api import categorias_nao_pai
#### DJANGO ######
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
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
from .serializers import UtilizadorSerializer, ConsumidorSerializer, FornecedorSerializer, ProdutoSerializer,UnidadeProducaoSerializer, VeiculoSerializer, CategoriaSerializer, ProdutoUnidadeProducaoSerializer, SingleProdutoPaginaSerializer, CarrinhoSerializer, ProdutosCarrinhoResponseSerializer, ProdutosCarrinhoRequestSerializer, ProdutoSerializerRequest, TemProdutoNoCarrinhoSerializer
### permissions.py ###
from .permissions import IsOwnerOrReadOnly, IsFornecedorOrReadOnly, IsFornecedorAndOwnerOrReadOnly, IsConsumidorAndOwnerOrReadOnly, IsConsumidorAndOwner
####
from decimal import Decimal







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
    def get(self, request, username, format=None):
        utilizador = self.get_object(username)
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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
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
    permission_classes= [IsFornecedorOrReadOnly,IsAuthenticatedOrReadOnly]
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
    """Devolve um produto na loja, mas procura por um id
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
    """Devolve todos os produtos que estão associados a uma unidade de produção. Mostra os produtos quer estejam
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
def getVeiculo(request, idVeiculo, idFornecedor, idUnidadeProducao, format=None):
    fornecedor = Fornecedor.objects.get(id=idFornecedor)
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
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializar.data,status=status.HTTP_200_OK)
    def post(self, request, username, format=None):
        if request.user.username != username:
            return Response({'detail':"Não tem permissão para realizar esta ação, porque não é o utilizador dono deste carrinho!"}, status=status.HTTP_401_UNAUTHORIZED)
        carrinho = self.get_carrinho(username)
        if 'carrinho' in request.data:
            if int(request.data['carrinho'])!=int(carrinho.id):
                return Response({'detail':'O ID do carrinho fornecido não corresponde ao id do carrinho do utilizador logado. Não precisa de enviar o id do carrinho, porque ele é atríbuido de acordo com o utilizador que está logado.'}, status=status.HTTP_400_BAD_REQUEST)
        serializador = ProdutosCarrinhoRequestSerializer(data=request.data)
        print("\n\n\n",serializador,"\n\n\n")
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
        print("\n\n\n\n",request.data,"\n\n\n\n")
        if item_carrinho is None:
            return Response({"detail": "Produto não encontrado no carrinho"},status=status.HTTP_404_NOT_FOUND)

        # Atualize o objeto com os novos dados
        data = request.data.copy()
        
        data['produto'] = item_carrinho.produto.id
        serializer = ProdutosCarrinhoRequestSerializer(item_carrinho, data=data)
        #print(serializer)
        if serializer.is_valid():
            print("peguei")
            produto = item_carrinho.produto
            #print(serializer)
            if produto.unidade_medida in ['kg','g','l','ml']:
                precoKilo = produto.preco_a_granel
                preco = Decimal(request.data['quantidade']) * precoKilo
            elif produto.unidade_medida in ['un']:
                precoKilo = produto.preco_por_unidade
                preco = Decimal(request.data['quantidade']) * precoKilo
            print("trinquei")
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
    

