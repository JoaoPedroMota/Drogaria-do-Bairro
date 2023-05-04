from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied



class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj != request.user:
            raise PermissionDenied(detail="Não pode atualizar/apagar um utilizador que não lhe pertence.")
        return True