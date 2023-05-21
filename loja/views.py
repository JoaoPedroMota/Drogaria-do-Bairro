from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests
from .models import Utilizador, Fornecedor, Consumidor, UnidadeProducao, Veiculo, Carrinho,Categoria, Produto
from django.contrib import messages
from django.contrib.auth import authenticate, login as AuthLogin, logout
from .forms import PasswordConfirmForm, UtilizadorFormulario, FornecedorFormulario, EditarPerfil, criarUnidadeProducaoFormulario, criarVeiculoFormulario, ProdutoForm, editarVeiculoFormulario, editarUnidadeProducaoFormulario
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import ConfirmacaoForm
import requests
from django.db.models import QuerySet
from django.contrib.auth.hashers import check_password
from loja.api.serializers import *

import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url = f"http://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


#     if request.user != utilizador:
#         return HttpResponse('Você não deveria estar aqui!')
#     if request.method == 'POST':
#         logout(request)
#         utilizador.delete()
#         return redirect('loja-home')
#     context={'objeto':utilizador, 'pagina':'apagar-conta'}
#     return render(request,'loja/delete.html', context)

# Create your views here.
def loja(request):
    context = {
        "session": request.session.get("user"),
        "pretty": json.dumps(request.session.get("user"), indent=4),
        
    }
    return render(request, 'loja/loja.html', context)

def auth0(request):
    context = {
        "session": request.session.get("user"),
        "pretty": json.dumps(request.session.get("user"), indent=4),
    }
    return render(request, 'loja/auth0.html', context)

def contacts(request):
    context = {}
    return render(request, 'loja/contacts.html', context)
def about(request):
    context = {}
    return render(request, 'loja/about.html', context)
def carrinho(request):
    context = {}
    return render(request, 'loja/carrinho.html', context)

def checkout(request):
    context = {}
    return render(request, 'loja/checkout.html', context)
def news(request):
    context = {}
    return render(request, 'loja/news.html', context)

def confirm_password_view(request):
    if request.method == 'POST':
        form = PasswordConfirmForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            username = request.user.username
            user = authenticate(username=username, password=password)

            if user is not None:
                pass
            else:
                # Password doesn't match, show an error message
                form.add_error('password', 'Incorrect password.')
    else:
        form = PasswordConfirmForm()
    
    context = {'form': form}
    return render(request, 'password_confirm.html', context)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("loja-callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    
    user_id = token['userinfo']['email']

    request.session['auth0_user_id'] = user_id

    user = Utilizador.objects.get(email=user_id)

    AuthLogin(request, user)

    return redirect(request.build_absolute_uri(reverse("loja-home")))

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("loja-home")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def registerUtilizador(request):
    pagina = 'registo'
    form = UtilizadorFormulario()
    
    if request.method == 'POST':
        formulario = UtilizadorFormulario(request.POST, request.FILES)
        if formulario.is_valid():
            utilizador = formulario.save(commit=False)
            utilizador.username = utilizador.username.lower()
            utilizador.cidade = utilizador.cidade.upper()
            utilizador.nome = utilizador.first_name+' '+ utilizador.last_name
            utilizador.save()
            AuthLogin(request,utilizador)
            if utilizador.tipo_utilizador == "C":
                consumidor = Consumidor.objects.create(utilizador=utilizador)
                carrinho = Carrinho.objects.create(consumidor=consumidor)
                return redirect('loja-home')
            else:
                Fornecedor.objects.create(utilizador=utilizador)
                return redirect('loja-home')

            
        else:
            messages.error(request,'Ocorreu um erro durante o processo de registo.')
            form = formulario  # reatribui o formulário com erros

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
    context = {'form':form}
    return render(request,'loja/register_fornecedor.html' ,context)

@login_required(login_url='loja-login')
def editarPerfil(request):
    pagina = 'editarPerfil'
    utilizador = request.user
    form = EditarPerfil(instance=utilizador)
    if request.method == 'POST':
        form = EditarPerfil(request.POST, request.FILES,instance = utilizador)
        username = request.POST.get('username')
        utilizador.first_name = request.POST.get('first_name')
        utilizador.last_name = request.POST.get('last_name')
        utilizador.nome = utilizador.first_name + ' ' + utilizador.last_name
        utilizador.email = request.POST.get('email')
        utilizador.pais = request.POST.get('pais')
        utilizador.cidade = request.POST.get('cidade')
        utilizador.telemovel = request.POST.get('telemovel')
        utilizador.imagem_perfil = request.POST.get('imagem_perfil')
        utilizador.username = username  
        if form.is_valid():
            utilizador = form.save(commit=False)
            utilizador.username = username.lower()
            utilizador.cidade = utilizador.cidade.upper()
            utilizador.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            link = reverse('loja-perfil', args=[request.user.username])
            return redirect(link)
    context = {'form':form, 'pagina':pagina}
    return render(request, 'loja/editarUtilizador.html', context)


@login_required(login_url='loja-login')
def apagarConta(request, pk):
    utilizador = Utilizador.objects.get(pk=pk)

    if request.user != utilizador:
        return HttpResponse('Você não deveria estar aqui!')

    if request.method == 'POST':
        password = request.POST.get('password')
        if check_password(password, utilizador.password):
            logout(request)
            utilizador.delete()
            return redirect('loja-home')
        else:
            messages.error(request, 'Senha incorreta. A conta não foi excluída.')

    context = {'objeto': utilizador, 'pagina': 'apagar-conta'}
    return render(request, 'loja/delete.html', context)

        

@login_required(login_url='loja-login')
def perfil(request, userName):
    utilizadorPerfil = Utilizador.objects.get(username=userName)
    pagina = 'perfil'
    context={'pagina':pagina, 'utilizadorView': utilizadorPerfil}
    if utilizadorPerfil.is_fornecedor:
        fornecedor = utilizadorPerfil.fornecedor
        unidadesProducao = fornecedor.unidades_producao.all()
        numero_up = unidadesProducao.count()
        context['unidadesProducao'] = unidadesProducao
        context['numero_up'] = numero_up
    return render(request,'loja/perfil.html',context)

@login_required(login_url='loja-login')
def criarUP(request, userName):
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor_id = utilizador.fornecedor
    pagina = 'criarUP'
    formulario = criarUnidadeProducaoFormulario()
    if request.user.is_fornecedor:
        if request.method == 'POST':
            formulario = criarUnidadeProducaoFormulario(request.POST)
            if formulario.is_valid():
                UnidadeProducao.objects.create(
                    fornecedor = fornecedor_id,
                    tipo_unidade = request.POST.get('tipo_unidade'),
                    nome = request.POST.get('nome'),
                    pais = request.POST.get('pais'),
                    cidade = request.POST.get('cidade'),
                    morada = request.POST.get('morada')
                )
                link = reverse('loja-perfil', args=[request.user.username])
                return redirect(link)
            else:
                messages.error(request,'Ocorreu um erro durante o processo de adição de uma Unidade de Produção')
    else:
        return HttpResponseForbidden()
    
    context = {'form':formulario, 'pagina':pagina}
    return render(request, 'loja/criarUP.html', context)



# def unidadeProducao(request, userName, id):
#     context = {}
#     utilizador = Utilizador.objects.get(username=userName)
#     fornecedor = utilizador.fornecedor
#     #fornecedor.unidades_producao.all()
#     unidadeProducao = fornecedor.unidades_producao.get(pk=id)
#     veiculos = unidadeProducao.veiculo_set.all()
#     print("\n\n\n\n",repr(veiculos))
#     num_veiculos = veiculos.count()
    
    
#     context={'veiculos':veiculos, 'num_veiculos':num_veiculos, 'unidadeProducao':unidadeProducao}
#     return render(request, 'loja/unidadeProducao.html', context)

#######################ZONA DE TESTE######################################################

def unidadeProducao(request, userName, id):
    context = {}
    # utilizador = Utilizador.objects.get(username=userName)
    # fornecedor = utilizador.fornecedor
    # #fornecedor.unidades_producao.all()
    # unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    # veiculos = unidadeProducao.veiculo_set.all()
    
    # num_veiculos = veiculos.count()
    #url = 'http://127.0.0.1:8000/api/fornecedores/'+str(userName)
    #url = 'http://127.0.0.1:8000/api/utilizadores/'
    
    #response = requests.get(url)
    
    #if response.status_code == 200:
    #    data = response.json()
    #    print("FJAOIWJFOIJAWIOFJIOAWJF",id)
        # Process the data as needed
        #return data
    #else:
        #print('Error:', response.status_code)
        #print('Response:', response.content)
    #    return None
    #("informaçao que fui buscar: ",data)              
    #print(data[0]['id'])
    #idFornecedor = data['id']

    url2 = 'http://127.0.0.1:8000/api/fornecedores/'+str(userName)+'/unidadesProducao/'+str(id)+'/veiculos/'
    #path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/veiculos/', views.getVeiculos),
    response2 = requests.get(url2)
    if response2.status_code == 200:
        data2 = response2.json()
        # Process the data as needed
        #return data
    else:
        #print('Error:', response2.status_code)
        #print('Response:', response2.content)
        return None

    print("informaçao que fui buscar 2: ",data2)
    num_veiculos = len(data2)
    print("num_veiculos",num_veiculos)
    veiculos = data2
    print("veiculos",veiculos)

    # queryset = QuerySet(model=veiculos, query=None, using='default')
    # queryset._result_cache = veiculos
    # print("\nprint the QUERYSET ",queryset)

    context={'veiculos':veiculos, 'num_veiculos':num_veiculos, 'unidadeProducao':id}
    return render(request, 'loja/unidadeProducao.html', context)

#######################ZONA DE TESTE######################################################

@login_required(login_url='loja-login')
def editarUnidadeProducao(request, userName, id):
    pagina = 'editarUnidadeProducao'
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor= utilizador.fornecedor
    unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    #veiculo = Veiculo.objects.get(pk=idVeiculo)
    form = editarUnidadeProducaoFormulario(instance=UnidadeProducao)
    if request.user.is_fornecedor:
        if request.method == 'POST':
            formulario = editarUnidadeProducaoFormulario(request.POST)
            if formulario.is_valid():
                unidadeProducao.nome = request.POST.get('nome')
                unidadeProducao.pais = request.POST.get('pais')
                unidadeProducao.cidade = request.POST.get('cidade')
                unidadeProducao.morada = request.POST.get('morada')
                unidadeProducao.tipo_unidade = request.POST.get('tipo_unidade')
                unidadeProducao.save()
                link = reverse('loja-perfil', args=[userName])
                return redirect(link)
            else:
                messages.error(request,'Ocorreu um erro durante o processo de edição de uma unidade de produção')
    else:
        return HttpResponseForbidden()
    
    context = {'form':formulario, 'pagina':pagina, 'unidadeProducao':unidadeProducao}
    return render(request, 'loja/editarUnidadeProducao.html', context)


def removerUnidadeProducao(request, userName, id):
    # Busca a unidade de produção pelo id passado na URL
    unidade_producao = UnidadeProducao.objects.get(pk=id)
    
    # Verifica se a unidade de produção pertence ao fornecedor logado
    if request.user == unidade_producao.fornecedor.utilizador:
        # Remove a unidade de produção
        unidade_producao.delete()
    
    # Redireciona para a página de perfil do fornecedor
    return redirect('loja-perfil', userName=request.user.username)


@login_required(login_url='loja-login')
def criarVeiculo(request, userName, id):
    pagina = 'criarVeiculo'
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor= utilizador.fornecedor
    unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    formulario = criarVeiculoFormulario()
    if request.user.is_fornecedor:
        if request.method == 'POST':
            formulario = criarVeiculoFormulario(request.POST)
            if formulario.is_valid():
                Veiculo.objects.create(
                    unidadeProducao = unidadeProducao,
                    tipo_veiculo = request.POST.get('tipo_veiculo'),
                    nome = request.POST.get('nome'),
                    estado_veiculo = Veiculo.disponivel
                )
                link = reverse('loja-unidadeProducao', args=[userName, id])
                return redirect(link)
            else:
                messages.error(request,'Ocorreu um erro durante o processo de adição de uma Unidade de Produção')
    else:
        return HttpResponseForbidden()
    
    context = {'form':formulario, 'pagina':pagina, 'unidadeProducao':unidadeProducao}
    return render(request, 'loja/criarVeiculo.html', context)

@login_required(login_url='loja-login')
def editarVeiculo(request, userName, id, idVeiculo):
    pagina = 'editarVeiculo'
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor= utilizador.fornecedor
    unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    veiculo = Veiculo.objects.get(pk=idVeiculo)
    form = editarVeiculoFormulario(instance=veiculo)
    if request.user.is_fornecedor:
        if request.method == 'POST':
            formulario = editarVeiculoFormulario(request.POST, instance = veiculo)
            if formulario.is_valid():
                veiculo.nome = request.POST.get('nome')
                veiculo.estado_veiculo = request.POST.get('estado_veiculo')
                veiculo.save()
                # Veiculo.objects.save(
                #     unidadeProducao = unidadeProducao,
                #     tipo_veiculo = veiculo.tipo_veiculo,
                #     nome = request.POST.get('nome'),
                #     estado_veiculo = request.POST.get('estado_veiculo')
                # )
                link = reverse('loja-unidadeProducao', args=[userName, id])
                return redirect(link)
            else:
                messages.error(request,'Ocorreu um erro durante o processo de edição de um veiculo')
    else:
        return HttpResponseForbidden()
    
    context = {'form':formulario, 'pagina':pagina, 'unidadeProducao':unidadeProducao}
    return render(request, 'loja/editarVeiculo.html', context)

def removerVeiculo(request, userName, id):
    veiculo = Veiculo.objects.get(id=id)
    veiculo.delete()
    return redirect(request.META['HTTP_REFERER'])

def remover_veiculo(request, id):
    veiculo = get_object_or_404(Veiculo, pk=id)
    if request.method == 'POST':
        form = ConfirmacaoForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['nome_veiculo'] != veiculo.nome:
                form.add_error(None, f'O nome do veículo a ser removido é {veiculo.nome}')
            else:
                veiculo.delete()
                messages.success(request, 'Veículo removido com sucesso.')
                return redirect('loja-unidadeProducao', request.user.username, veiculo.unidade_producao.id)
    else:
        form = ConfirmacaoForm()
    return render(request, 'loja/removerVeiculo.html', {'form': form, 'veiculo': veiculo})



# #esta aqui mas depois tem que ir para o cimo
# from django.shortcuts import render, redirect
# from .models import UnidadeProducao, Produto, Categoria, Marca
# from .forms import ProdutoForm

# def criar_produto(request, userName, id):
#     unidade = UnidadeProducao.objects.get(pk=id)
#     if request.method == 'POST':
#         form = ProdutoForm(request.POST)
#         if form.is_valid():
#             produto = form.save(commit=False)
#             categoria_nome = form.cleaned_data['categoria']
#             categoria, _ = Categoria.objects.get_or_create(nome=categoria_nome)
#             produto.categoria = categoria
#             marca_nome = form.cleaned_data['marca']
#             marca, _ = Marca.objects.get_or_create(nome=marca_nome)
#             produto.marca = marca
#             produto.unidade_producao = unidade
#             produto.save()
#             messages.success(request, 'Produto criado com sucesso!')
#             return redirect('loja-unidadeProducao', userName=userName, id=id)
#     else:
#         form = ProdutoForm()
#     return render(request, 'loja/criar_produto.html', {'form': form})

# #ainda nao estah a ser usado
# def ver_produtos(request):
#     produtos = Produto.objects.all()
#     context = {'produtos': produtos}
#     return render(request, 'ver_produtos.html', context)


def criar_produto(request, userName, id):
    unidade = get_object_or_404(UnidadeProducao, pk=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            categoria_nome = form.cleaned_data['categoria']
            categoria, _ = Categoria.objects.get_or_create(nome=categoria_nome)
            produto.categoria = categoria
            produto.unidade_producao = unidade
            produto.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('loja-unidadeProducao', userName=userName, id=id)
    else:
        form = ProdutoForm()
    return render(request, 'loja/criar_produto.html', {'form': form})




def lista_produtos_eletronicos(request):
    eletronicos = Categoria.objects.get(nome='Eletrónicos')
    produtos = Produto.objects.filter(categoria=eletronicos)
    return render(request, 'lista_produtos.html', {'produtos': produtos})

def ver_produtos(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    url = 'http://127.0.0.1:8000/api/produtos/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        return None

    url2 = 'http://127.0.0.1:8000/api/produtos_loja/'
    response2 = requests.get(url2)
    if response2.status_code == 200:
        data2 = response2.json()
    else:
        return None

    FilteredProducts = []
    for product in data:
        if q.lower() in str(product['nome']).lower() or q.lower() in str(product['categoria']).lower():
            FilteredProducts.append(product)

    actualFilteredProducts = []
    for product in FilteredProducts:
        for shopProduct in data2:
            if product['id'] == shopProduct['produto']:
                if shopProduct['preco_a_granel']==None:
                    actualFilteredProducts.append({'produto':product['nome'], 'preco':shopProduct['preco_por_unidade'],'tipo':"unidade"})
                else:
                    actualFilteredProducts.append({'produto':product['nome'], 'preco':shopProduct['preco_a_granel'],'tipo':"granel"})

    context={'produtos_precos':actualFilteredProducts}
    return render(request, 'loja/shop.html', context)