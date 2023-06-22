from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def fornecedor_required(view_func):
    @login_required(login_url='loja-login')
    def wrapper(request, *args, **kwargs):
        fornecedor = request.user.fornecedor if hasattr(request.user, 'fornecedor') else None
        if fornecedor is not None:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('loja-perfil', userName=request.user.username)
    return wrapper



def consumidor_required(view_func):
    @login_required(login_url='loja-login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_consumidor:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('loja-perfil', userName=request.user.username)
    return wrapper
