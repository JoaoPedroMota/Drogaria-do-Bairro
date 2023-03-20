from django.shortcuts import redirect, render
from .models import Utilizador, Fornecedor, Consumidor
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UtilizadorFormulario, FornecedorFormulario
from django.contrib.auth.decorators import login_required


# Create your views here.
def loja(request):
    context = {}
    return render(request, 'loja/loja.html', context)

def carrinho(request):
    context = {}
    return render(request, 'loja/carrinho.html', context)

def checkout(request):
    context = {}
    return render(request, 'loja/checkout.html', context)


def loginUtilizador(request):
    pagina='login'
    if request.user.is_authenticated:
        print("entrei")
        return redirect('loja-home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            utilizador = Utilizador.objects.get(email=email)
        except:
            messages.error(request,"Este email não corresponde a nenhum utilizador registado")
        utilizador = authenticate(request, email=email, password=password)
        if utilizador is not None:
            login(request, utilizador)
            return redirect('loja-home')
        else:
            messages.error(request,"Utilizador ou password errados")  
    context = {'pagina':pagina}
    return render(request, 'loja/login_register.html', context)


def registerUtilizador(request):
    pagina = 'registo'
    form = UtilizadorFormulario()
    
    if request.method == 'POST':
        formulario = UtilizadorFormulario(request.POST, request.FILES)
        if formulario.is_valid():
            utilizador = formulario.save(commit=False)
            utilizador.username = utilizador.username.lower()
            utilizador.pais = utilizador.pais.upper()
            utilizador.cidade = utilizador.cidade.upper()
            utilizador.save()
            login(request,utilizador)
            if utilizador.tipo_utilizador == "C":
                consumidor = Consumidor.objects.create(utilizador=utilizador)
                return redirect('loja-home')
            else:
                return redirect('loja-form-forcedor')

            
        else:
            messages.error(request,'Ocorreu um erro durante o processo de registo.')
    context = {'pagina': pagina, 'form': form}
    return render(request,'loja/login_register.html', context)

def formFornecedor(request):
    form = FornecedorFormulario()
    if request.method == 'POST':
        formulario = FornecedorFormulario(request.POST)
        if formulario.is_valid():
            Fornecedor.objects.create(
                utilizador = request.user,
                descricao = request.POST.get('descricao')
            )
            return redirect('loja-home')
        else:
            messages.error(request,'Ocorreu um erro durante o processo de registo')
    context = {'formulario':form}
    return render(request,'loja/register_fornecedor.html' ,context)

def logutUtilizador(request):
    logout(request)
    return redirect('loja-home')