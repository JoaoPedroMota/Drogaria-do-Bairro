from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from loja.models import *

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        username = view.kwargs.get('username')
        if username != request.user.username:
            raise PermissionDenied(detail="Não pode ler/atualizar/apagar um utilizador que não o seu.")
        return True
        


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj != request.user:
            raise PermissionDenied(detail="Não pode atualizar/apagar um utilizador que não lhe pertence.")
        return True
    
    
class IsFornecedorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.is_fornecedor:
            return True
        raise PermissionDenied(detail="Não pode realizar esta ação porque não é um fornecedor")
    
    
    
class IsFornecedorAndOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.is_fornecedor:
            username = view.kwargs.get('username') #username no link.

            user = Utilizador.objects.get(username=username) # a que utilizador corresponde o username no link

            idFornecedor = user.fornecedor.id #qual o fornecedor que tem como username, o username no link

            idUnidadeProducao = view.kwargs.get('idUnidadeProducao') #id unidade de producao está indicada no link

            try:
                up = UnidadeProducao.objects.get(id=idUnidadeProducao) #unidade producao com o id que está no link
                return up.fornecedor.utilizador == request.user and up.fornecedor.id == int(idFornecedor) #se o fornecedor(utilizador) da up indicada no link
                                                                                                        # for o mesmo utilizador do request e o id do fornecedor 
                                                                                                        # da up indicada no link for o mesmo id do fornecedor do utilizador indicado no link
                                                                                                        #
            except UnidadeProducao.DoesNotExist:
                return False
        raise PermissionDenied(detail="Não pode realizar esta ação porque não é um fornecedor")




class IsFornecedorAndOwner2(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_fornecedor:
            username = view.kwargs.get('username') #username no link.

            user = Utilizador.objects.get(username=username) # a que utilizador corresponde o username no link

            idFornecedor = user.fornecedor.id #qual o fornecedor que tem como username, o username no link

            idUnidadeProducao = view.kwargs.get('idUnidadeProducao') #id unidade de producao está indicada no link

            try:
                up = UnidadeProducao.objects.get(id=idUnidadeProducao) #unidade producao com o id que está no link
                return up.fornecedor.utilizador == request.user and up.fornecedor.id == int(idFornecedor) #se o fornecedor(utilizador) da up indicada no link
                                                                                                        # for o mesmo utilizador do request e o id do fornecedor 
                                                                                                        # da up indicada no link for o mesmo id do fornecedor do utilizador indicado no link
                                                                                                        #
            except UnidadeProducao.DoesNotExist:
                return False
        raise PermissionDenied(detail="Não pode realizar esta ação porque não é um fornecedor")



class IsFornecedorAndOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_fornecedor:
            idFornecedor = view.kwargs.get('idFornecedor')
            idUnidadeProducao = view.kwargs.get('idUnidadeProducao')
            try:
                up = UnidadeProducao.objects.get(id=idUnidadeProducao)
                return up.fornecedor.utilizador == request.user and up.fornecedor.id == int(idFornecedor)
            except UnidadeProducao.DoesNotExist:
                return False
        raise PermissionDenied(detail="Não pode realizar esta ação porque não é um fornecedor")

class IsConsumidorAndOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if not request.user.is_consumidor:
                raise PermissionDenied(detail="Não é um consumidor autenticado")
            if request.user.is_consumidor:
                username = view.kwargs.get('username')
                user = Utilizador.objects.get(username=username)
                idConsumidor = user.consumidor.id
                idCarrinho = user.consumidor.carrinho.id
                try:
                    cart = Carrinho.objects.get(id=idCarrinho)
                    return cart.consumidor.utilizador == request.user and cart.consumidor.id == int(idConsumidor)
                except Carrinho.DoesNotExist:
                    return False
        raise PermissionDenied(detail='Não pode ver ou editar os produtos que estão no carrinho de outro consumidor. Não é o consumidor dono deste carrinho')

class IsConsumidorAndOwner2(permissions.BasePermission):
    def has_permission(self,request, view):
        if request.user.is_authenticated:
            if not request.user.is_consumidor:
                raise PermissionDenied(detail="Não é um consumidor autenticado")
            # if request.user.is_superuser:
            #     if request.method in permissions.SAFE_METHODS:
            #         return True
            #     else:
            #         raise PermissionDenied(detail="Está logado enquanto admin")
            if request.user.is_consumidor:
                username = view.kwargs.get('username')
                user = Utilizador.objects.get(username=username)
                userLogadoConsumidor = request.user.consumidor
                userConsumidorRequestURL = user.consumidor
                return int(userLogadoConsumidor.id) == int(userConsumidorRequestURL.id)
        raise PermissionDenied(detail='Não pode aceder/criar/editar esta informações. Não lhe pertence/tem autorização. Autentique-se com a conta do seu consumidor!')
                



class IsConsumidorAndOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self,request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if not request.user.is_consumidor:
                raise PermissionDenied(detail="Não é um consumidor autenticado!")
            if request.user.is_consumidor:
                username = view.kwargs.get('username')
                user = Utilizador.objects.get(username=username)
                idConsumidor = user.consumidor.id
                idCarrinho = user.consumidor.carrinho.id
                try:
                    cart = Carrinho.objects.get(id=idCarrinho)
                    return cart.consumidor.utilizador == request.user and cart.consumidor.id == int(idConsumidor)
                except Carrinho.DoesNotExist:
                    return False
        raise PermissionDenied(detail='Não pode ver ou editar os produtos que estão no carrinho de outro consumidor. Não é o consumidor dono deste carrinho')
