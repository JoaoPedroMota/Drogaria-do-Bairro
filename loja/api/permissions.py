from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from loja.models import *

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
            idFornecedor = view.kwargs.get('idFornecedor')
            idUnidadeProducao = view.kwargs.get('idUnidadeProducao')
            try:
                up = UnidadeProducao.objects.get(id=idUnidadeProducao)
                return up.fornecedor.utilizador == request.user and up.fornecedor.id == int(idFornecedor)
            except UnidadeProducao.DoesNotExist:
                return False
        raise PermissionDenied(detail="Não pode realizar esta ação porque não é um fornecedor")
