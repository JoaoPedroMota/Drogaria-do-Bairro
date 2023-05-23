from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def fornecedor_required(view_func):
    @login_required(login_url='loja-login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_fornecedor:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('loja-perfil', userName=request.user.username)
    return wrapper