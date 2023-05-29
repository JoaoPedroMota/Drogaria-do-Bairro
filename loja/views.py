from decimal import Decimal
from datetime import date
import requests
import json
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.middleware.csrf import get_token
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import PasswordConfirmForm, ProdutoUnidadeProducaoForm, UtilizadorFormulario, FornecedorFormulario, EditarPerfil, criarUnidadeProducaoFormulario, criarVeiculoFormulario, ProdutoForm, editarVeiculoFormulario, editarUnidadeProducaoFormulario, CompletarPerfil
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import ConfirmacaoForm
import requests
from django.db.models import QuerySet
from django.contrib.auth.hashers import check_password
from loja.api.serializers import *
from .utils import fornecedor_required


import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

from loja.api.serializers import UtilizadorSerializer

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
    context = {}
    if request.user.is_authenticated and request.user.is_consumidor:
        if request.session.get('carrinho') is not None and request.session.get('carrinho') !={}:
            adicionarProdutosCarrinhoDpsDeLogar(request)
    elif request.user.is_authenticated and request.user.is_fornecedor:
        if request.session.get('carrinho') is not None and request.session.get('carrinho') !={}:
            request.session['carrinho'] = {}
    return render(request, 'loja/loja.html', context)
def contacts(request):
    context = {}
    return render(request, 'loja/contacts.html', context)
def about(request):
    context = {}
    return render(request, 'loja/about.html', context)
# def carrinho(request):

#     if request.user.is_authenticated:
#             if request.user.is_consumidor:
#                 consumidor = request.user.username
#                 carrinho, created = Carrinho.objects.get_or_create(consumidor=consumidor, complete=False)
#                 items = carrinho.adicionar_ao_carrinho.all()
#     else:
#         items = []
#     context = {'items':ProdutosCarrinho}
#     return render(request, 'loja/carrinho.html', context)

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

def loginUtilizador(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("loja-callback"))
    )


def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    username = token['userinfo']['nickname']
    email = token['userinfo']['email']

    user, created = Utilizador.objects.get_or_create(username=username, email=email)

    login(request, user)

    if created:
        return redirect('loja-completarPerfil')
    else:
        return redirect(request.build_absolute_uri(reverse("loja-home")))

    # username = token['userinfo']['nickname']

    # # url = f'http://127.0.0.1:8000/api/utilizadores/{username}'
    # url = f'http://127.0.0.1:8000/api/utilizadores/ninfante'
    
    # response = requests.get(url)

    # if response.status_code == 200:
    #     print('AAAA\n\n')
    #     print(response.json())
    #     utilizador = UtilizadorSerializer(data=response.json())
    #     login(request, utilizador)
    #     return redirect(request.build_absolute_uri(reverse("loja-home")))
    # else:
    #     print('BBBB\n\n')


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

# def registerUtilizador(request):
#     pagina = 'registo'
#     form = UtilizadorFormulario()
    
#     if request.method == 'POST':
#         formulario = UtilizadorFormulario(request.POST, request.FILES)
#         if formulario.is_valid():
#             utilizador = formulario.save(commit=False)
#             utilizador.username = utilizador.username.lower()
#             utilizador.cidade = utilizador.cidade.upper()
#             utilizador.nome = utilizador.first_name+' '+ utilizador.last_name
#             utilizador.save()
#             login(request,utilizador)
#             if utilizador.tipo_utilizador == "C":
#                 consumidor = Consumidor.objects.create(utilizador=utilizador)
#                 carrinho = Carrinho.objects.create(consumidor=consumidor)
#                 return redirect('loja-home')
#             else:
#                 Fornecedor.objects.create(utilizador=utilizador)
#                 return redirect('loja-home')

            
#         else:
#             messages.error(request,'Ocorreu um erro durante o processo de registo.')
#             form = formulario  # reatribui o formulário com erros

#     context = {'pagina': pagina, 'form': form}
#     return render(request,'loja/login_register.html', context)

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
def completarPerfil(request):
    utilizador = request.user
    form = CompletarPerfil(instance=utilizador)
    if request.method == 'POST':
        form = CompletarPerfil(request.POST, request.FILES,instance = utilizador)
        if form.is_valid():
            utilizador = form.save(commit=False)
            utilizador.username = request.POST.get('username').lower()
            utilizador.first_name = request.POST.get('first_name')
            utilizador.last_name = request.POST.get('last_name')
            utilizador.nome = utilizador.first_name + ' ' + utilizador.last_name
            utilizador.pais = request.POST.get('pais')
            utilizador.cidade = request.POST.get('cidade').lower()
            utilizador.telemovel = request.POST.get('telemovel')
            if request.POST.get('imagem_perfil'):
                utilizador.imagem_perfil = request.POST.get('imagem_perfil')
            utilizador.tipo_utilizador = request.POST.get('tipo_utilizador')
            utilizador.save()
            if utilizador.tipo_utilizador == "C":
                consumidor = Consumidor.objects.create(utilizador=utilizador)
                carrinho = Carrinho.objects.create(consumidor=consumidor)
            else:
                Fornecedor.objects.create(utilizador=utilizador)


            return redirect('loja-home')
    context = {'form':form}
    return render(request, 'loja/completarPerfil.html', context)

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

# @login_required(login_url='loja-login')
@fornecedor_required
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

# def ver_produtos(request):
#     q = request.GET.get('q') if request.GET.get('q') != None else ''
#     url = 'http://127.0.0.1:8000/api/produtos/'
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#     else:
#         return None

#     url2 = 'http://127.0.0.1:8000/api/produtos_loja/'
#     response2 = requests.get(url2)
#     if response2.status_code == 200:
#         data2 = response2.json()
#     else:
#         return None

#     FilteredProducts = []
#     for product in data:
#         if q.lower() in str(product['nome']).lower() or q.lower() in str(product['categoria']).lower():
#             FilteredProducts.append(product)

#     actualFilteredProducts = []
#     for product in FilteredProducts:
#         for shopProduct in data2:
#             if product['id'] == shopProduct['produto']:
#                 if shopProduct['preco_a_granel']==None:
#                     actualFilteredProducts.append({'produto':product['nome'], 'preco':shopProduct['preco_por_unidade'],'tipo':"unidade"})
#                 else:
#                     actualFilteredProducts.append({'produto':product['nome'], 'preco':shopProduct['preco_a_granel'],'tipo':"granel"})

#     context={'produtos_precos':actualFilteredProducts}
#     return render(request, 'loja/shop.html', context)


@fornecedor_required
def unidadeProducao(request, userName, id):
    context = {}
    def criar_produto_temporario(produtosUPRespostaJSON):
        lista_produtos_up = []
        nome_up = ""
        semaforo = 0
        #print("\n\n\n\nPRODUTOS RECEBIDOS. VIERAM DA API:",produtosUPRespostaJSON)
        for produto in produtosUPRespostaJSON:
            ### TABELA PRODUTO
            idProduto = produto.get('produto')
            urlProduto = f'http://127.0.0.1:8000/api/produtosID/{idProduto}/'
            respostaProdutoGeral = requests.get(urlProduto)
            produtoDicionario = respostaProdutoGeral.json() #informações de um produto


            
            #print(f"PRODUTO DICIONÁRIO:{produtoDicionario}")
            
            
            
            #### TABELA CATEGORIA
            
            
            nomeCategoria = produtoDicionario['categoria']['nome']
            
            
            

            # urlCategoria = f'http://127.0.0.1:8000/api/categoriaNome/{nomeCategoria}/'
        
            # respostaCategoria = requests.get(urlCategoria) #informacoes de uma categoria

            # categoriaDicionario = respostaCategoria.json()


            categoria = Categoria.objects.get(nome=nomeCategoria) #problema com loop de categoria pai
            
            
            
        
            
            #### DE VOLTA TABELA PRODUTO
            produtoDicionario['categoria'] = categoria
            
            
            produtoGeral = Produto(**produtoDicionario)  #cria um objeto produto sem guardar
            produto['produto'] = produtoGeral

            
            
            ##### TABELA UNIDADE PRODUÇÃO
            idUP = produto['unidade_producao']
            urlUP = f'http://127.0.0.1:8000/api/unidadesProducao/{idUP}'
            respostaUP = requests.get(urlUP)
            upDicionario = respostaUP.json() #informações de um produto
            
            
            
            ##### TABELA FORNECEDORES
            usernameFornecedor = upDicionario['fornecedor']['utilizador']
            
            urlFornecedor = f'http://127.0.0.1:8000/api/{usernameFornecedor}/fornecedor/'
            urlUtilizadorFornecedor = f'http://127.0.0.1:8000/api/{usernameFornecedor}/utilizadores/'
            
            
            respostaFornecedor = requests.get(urlFornecedor)
            respostaUtilizador = requests.get(urlUtilizadorFornecedor)
            
            dicionarioFornecedor = respostaFornecedor.json()
            dicionarioUtilizador = respostaUtilizador.json()
            
            
            
            user_temp = Utilizador(**dicionarioUtilizador)
            dicionarioFornecedor['utilizador'] = user_temp
            
            fornecedor_temp = Fornecedor(**dicionarioFornecedor)
            
            
            upDicionario['fornecedor'] = fornecedor_temp
            up_temporario = UnidadeProducao(**upDicionario)           
            
            
            if semaforo == 0:
                nome_up = up_temporario.nome
            
            produto['unidade_producao']=up_temporario
            
            
            
            
            #### TABELA ProdutoUnidadeProducao
            myProduto = ProdutoUnidadeProducao(**produto) #cria um produto unidade producao sem guardar
            lista_produtos_up.append(myProduto)
            #print(f"\n\n\n\nPRODUTO DICIONÁRIO UM SÓ PRODUTO:{produtoDicionario}")
        #print(f"\n\n\n\nLista de todos os produtos desta Unidade de Produção: {lista_produtos_up}")
        
        return lista_produtos_up, nome_up
    
    if True: #esconder codigo abaixo
        pass
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

    url2 = 'http://127.0.0.1:8000/api/'+str(userName)+'/fornecedor/unidadesProducao/'+str(id)+'/veiculos/'
    response2 = requests.get(url2)
    if response2.status_code == 200:
        data2 = response2.json()
        # Process the data as needed
        #return data
    else:
        #print('Error:', response2.status_code)
        #print('Response:', response2.content)
        return None

    #print("informaçao que fui buscar 2: ",data2)
    num_veiculos = len(data2)
    #print("num_veiculos",num_veiculos)
    veiculos = data2
    #print("veiculos",veiculos)

    
    
    ######produtos
    urlProdutosUP = f'http://127.0.0.1:8000/api/{userName}/fornecedor/unidadesProducao/{id}/produtos/'
    
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    respostaProdutosUP = sessao.get(urlProdutosUP)
    produtosUP = respostaProdutosUP.json()
    lista_produtos_up,nome_up = criar_produto_temporario(produtosUP)
    
    
    context={'veiculos':veiculos, 'num_veiculos':num_veiculos, 'unidadeProducao':id, "produtosUP":lista_produtos_up, 'nome_up':nome_up}
    return render(request, 'loja/unidadeProducao.html', context)

#######################ZONA DE TESTE######################################################

# @login_required(login_url='loja-login')
@fornecedor_required
def editarUnidadeProducao(request, userName, id):
    pagina = 'editarUnidadeProducao'
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor= utilizador.fornecedor
    unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    #veiculo = Veiculo.objects.get(pk=idVeiculo)
    form = editarUnidadeProducaoFormulario(instance=unidadeProducao)
    if request.user.is_fornecedor:
        if request.method == 'POST':
            form = editarUnidadeProducaoFormulario(request.POST, request.FILES,instance = unidadeProducao)
            if form.is_valid():
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
    
    context = {'form':form, 'pagina':pagina, 'unidadeProducao':unidadeProducao}
    return render(request, 'loja/editarUnidadeProducao.html', context)

# @login_required(login_url='loja-login')
# def editarPerfil(request):
#     pagina = 'editarPerfil'
#     utilizador = request.user
#     form = EditarPerfil(instance=utilizador)
#     if request.method == 'POST':
#         form = EditarPerfil(request.POST, request.FILES,instance = utilizador)
#         username = request.POST.get('username')
#         utilizador.first_name = request.POST.get('first_name')
#         utilizador.last_name = request.POST.get('last_name')
#         utilizador.nome = utilizador.first_name + ' ' + utilizador.last_name
#         utilizador.email = request.POST.get('email')
#         utilizador.pais = request.POST.get('pais')
#         utilizador.cidade = request.POST.get('cidade')
#         utilizador.telemovel = request.POST.get('telemovel')
#         utilizador.imagem_perfil = request.POST.get('imagem_perfil')
#         utilizador.username = username  
#         if form.is_valid():
#             utilizador = form.save(commit=False)
#             utilizador.username = username.lower()
#             utilizador.cidade = utilizador.cidade.upper()
#             utilizador.save()
#             messages.success(request, 'Perfil atualizado com sucesso.')
#             link = reverse('loja-perfil', args=[request.user.username])
#             return redirect(link)
#     context = {'form':form, 'pagina':pagina}
#     return render(request, 'loja/editarUtilizador.html', context)
@fornecedor_required
def removerUnidadeProducao(request, userName, id):
    # Busca a unidade de produção pelo id passado na URL
    unidade_producao = UnidadeProducao.objects.get(pk=id)
    
    # Verifica se a unidade de produção pertence ao fornecedor logado
    if request.user == unidade_producao.fornecedor.utilizador:
        # Remove a unidade de produção
        unidade_producao.delete()
    
    # Redireciona para a página de perfil do fornecedor
    return redirect('loja-perfil', userName=request.user.username)


# @login_required(login_url='loja-login')
@fornecedor_required
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

#@login_required(login_url='loja-login')
@fornecedor_required
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



@fornecedor_required
def removerVeiculo(request, userName, id):
    veiculo = Veiculo.objects.get(id=id)
    veiculo.delete()
    return redirect(request.META['HTTP_REFERER'])






#### O QUE É ISTO??????????????
@fornecedor_required
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

# @login_required(login_url='loja-login')
@fornecedor_required
def criar_produto(request, userName):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            nome_produto = form.cleaned_data['nome']
            idCategoria = form.data['categoria']
            urlCategoria = f'http://127.0.0.1:8000/api/categorias/{idCategoria}/'
            respostaCategoria = requests.get(urlCategoria)
            conteudo = respostaCategoria.json()
            
            categoria_nome = conteudo.get('nome')
            produto_data = {
                "nome": nome_produto,
                "categoria": categoria_nome
            }
            # print("DICIONÁRIO INFO:",produto_data)
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)
            urlCriarProduto = f"http://127.0.0.1:8000/api/produtos/"
            
            headers = {"Authorization": f"Token {request.user.auth_token}"}
            
            
            resposta = sessao.post(urlCriarProduto, data=produto_data, headers=headers)
            if resposta.status_code == 201:
                messages.success(request, 'Produto criado com sucesso!')
                return redirect('loja-perfil', userName=userName)
            else:
                print("ERRO!!!!!!!!")
                messages.error(request, 'Erro ao criar Produto!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}_error::{error}')
    else:
        form = ProdutoForm()
    return render(request, 'loja/criar_produto.html', {'form': form})




def lista_produtos_eletronicos(request):
    eletronicos = Categoria.objects.get(nome='Eletrónicos')
    produtos = Produto.objects.filter(categoria=eletronicos)
    return render(request, 'lista_produtos.html', {'produtos': produtos})


def sP(request,produto_id):
    
    filtered_products=[]
    idProdutoInt=int(produto_id)
    url = f'http://127.0.0.1:8000/api/produtos_loja/'
    response = requests.get(url)
    if response.status_code == 200:
        produtosNaLoja = response.json()
    else:
        return None
    listaID=[]

    for product in produtosNaLoja:
        if product['produto'] == idProdutoInt:
            listaID.append(product['id'])
    
    for i in listaID:
        url = f'http://127.0.0.1:8000/api/produtos_loja/{i}/'
        response = requests.get(url)
        if response.status_code == 200:
            infoSingleProduct = response.json()
            for product in produtosNaLoja:
                if product['id'] == i:
                    filtered_products.append({
                        'id':infoSingleProduct['id'],
                        'nome': infoSingleProduct['produto']['nome'],
                        'stock': product['stock'],
                        'descricao': product['descricao'],
                        'categoria': infoSingleProduct['produto']['categoria']['nome'],
                        'up': infoSingleProduct['unidade_producao']['nome'],
                        'fornecedor': infoSingleProduct['unidade_producao']['fornecedor']['utilizador'],
                        'morada': infoSingleProduct['unidade_producao']['morada'],
                        'pais': infoSingleProduct['unidade_producao']['pais'],
                        'cidade': infoSingleProduct['unidade_producao']['cidade'],
                        'dataP': infoSingleProduct['data_producao'],
                        'marca': infoSingleProduct['marca'],
                        'precoU':infoSingleProduct['preco_por_unidade'],
                        'precoG':infoSingleProduct['preco_a_granel'],
                        'unidade_medida': infoSingleProduct['unidade_medida'],
                        'quantidade_por_unidade': infoSingleProduct['quantidade_por_unidade'] if infoSingleProduct['quantidade_por_unidade'] is not None else '',
                        'unidade_Medida_Por_Unidade': infoSingleProduct['unidade_Medida_Por_Unidade'],
                        'imagem_produto': infoSingleProduct['imagem_produto'],
                    })

        else:
            return None


    context={'filtered_products':filtered_products}
    return render(request, 'loja/single-product.html',context)
    # url = f'http://127.0.0.1:8000/api/produtos_loja/{p}/'
    # response = requests.get(url)
    # if response.status_code == 200:
    #     data = response.json()
    # else:
    #     return None
    
    # if data['quantidade_por_unidade']==None:
    #     context={'produto_info':data['produto']['nome'],'categoria':data['produto']['categoria']['nome'],'granel':data['preco_a_granel'],'fornecedor':data['unidade_producao']['fornecedor']['utilizador'],'up':data['unidade_producao']['nome'],
    #              'morada':data['unidade_producao']['morada'],
    #              'cidade':data['unidade_producao']['cidade'],'pais':data['unidade_producao']['pais'],'descricao':data['descricao'],'unidadeM':'Kilograma','stock':data['stock']
    #              ,'data_producao':data['data_producao'],'marca':data['marca'],'unidade':data['preco_por_unidade']}
    # if data['preco_a_granel']==None:
    #     context={'produto_info':data['produto']['nome'],'categoria':data['produto']['categoria']['nome'],'granel':data['preco_a_granel'],'fornecedor':data['unidade_producao']['fornecedor']['utilizador'],'up':data['unidade_producao']['nome'],
    #              'morada':data['unidade_producao']['morada'],
    #              'cidade':data['unidade_producao']['cidade'],'pais':data['unidade_producao']['pais'],'descricao':data['descricao'],'unidadeM':'Unidade','stock':data['stock'],'data_producao':data['data_producao']
    #              ,'marca':data['marca'],'unidade':data['preco_por_unidade']}

    # return render(request, 'loja/single-product.html', context)
    
#  if shopProduct['preco_a_granel']==None:
#                     actualFilteredProducts.append({'produto':product['nome'], 'preco':shopProduct['preco_por_unidade'],'tipo':"unidade",'id':shopProduct['id']})
#                 else:
#                     actualFilteredProducts.append({'produto':product['nome'], 'preco':shopProduct['preco_a_granel'],'tipo':"granel",'id':shopProduct['id']})


def ver_produtos(request):
    if not request.user.is_authenticated or (request.user.is_authenticated and request.user.is_consumidor):
        q = request.GET.get('q', '')  # Usando o operador de coalescência nula para definir um valor padrão vazio para 'q'
        url = 'http://127.0.0.1:8000/api/produtos/'
        info = {'q': q}
        response = requests.get(url, data=info)
        if response.status_code == 200:
            data = response.json()
        else:
            data=[]
       
        url2 = 'http://127.0.0.1:8000/api/produtos_loja/'
        info = {'q': q}
        response2 = requests.get(url2, data=info)
        if response2.status_code == 200:
            data2 = response2.json()
        else:
            data2=[]
        
        FilteredProducts = []
        for product in data:
            if q.lower() in str(product['nome']).lower() or q.lower() in str(product['categoria']).lower():
                FilteredProducts.append(product)
        
        actualFilteredProducts = []
       
        for product in FilteredProducts:
            prices = []
            prices1 = []

            for shopProduct in data2:
                if product['id'] == shopProduct['produto']:
                    if shopProduct['preco_a_granel'] is not None:
                        prices.append(shopProduct['preco_a_granel'])
                    else:
                        prices1.append(shopProduct['preco_por_unidade'])

            min_price = min(prices) if prices and None not in prices else -1
            min_price1 = min(prices1) if prices1 and None not in prices1 else -1
            if prices or prices1:
                product_info = {
                    'id': product['id'],
                    'produto': product['nome'],
                    'min_precoG': min_price,
                    'min_precoU': min_price1,
                    'categoria': product['categoria']['nome'],
                    'idCategoria': product['categoria']['id'],
                    'imagem_produto': None
                }
                lowest_price_product = None
                if min_price != -1:
                    lowest_price_product = next(
                        (shopProduct for shopProduct in data2 if shopProduct['preco_a_granel'] == min_price), None)
                elif min_price1 != -1:
                    lowest_price_product = next(
                        (shopProduct for shopProduct in data2 if shopProduct['preco_por_unidade'] == min_price1), None)

                if lowest_price_product is not None:
                    product_info['imagem_produto'] = lowest_price_product['imagem_produto']

                actualFilteredProducts.append(product_info)
        
        context = {'produtos_precos': actualFilteredProducts, 'termo_pesquisa': q}
        return render(request, 'loja/shop.html', context)

# def adicionar_ao_carrinho(request, produto_id):
#     quantidade = request.GET.get('quantidade')
#     print(produto_id)
#     print(quantidade)
#     context = {}
#     return redirect('loja-ver_produtos')






##################################################

def carrinho(request):
    # if request.session.get('carrinho') is not None and request.session.get('carrinho') != {}:
    #     print(request.session['carrinho'])
    context = {}
    if request.user.is_authenticated:
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)
        url = f"http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/"
        resposta = sessao.get(url)
        if resposta.content:
            conteudo = resposta.json()
            total= Decimal(0)
            produtos = []
            for produto in conteudo:
                produtoUP = produto['produto']
                idParaReceberNome = produtoUP['produto']
                urlNomeProduto = f'http://127.0.0.1:8000/api/produtosID/{idParaReceberNome}/'
                resposta = sessao.get(urlNomeProduto)
                nome = resposta.json()
                nomeProduto = nome['nome']
                quantidade = produto['quantidade']
                precoKilo = produto['precoKilo']
                preco = produto['preco']
                idProdutoNoCarrinho = produto['id']
                total+=Decimal(preco)
                produtos.append({
                    'produto' : produtoUP,
                    'nomeProduto': nomeProduto,
                    'quantidade':quantidade,
                    'precoKilo':precoKilo,
                    'preco':preco,
                    'idNoCarrinho':idProdutoNoCarrinho
                })
            # carrinho = Carrinho.objects.get(consumidor=request.user.consumidor)
            # produtos_carrinho = carrinho.produtos_carrinho.all()
            #total_price = sum(produto_carrinho.preco if produto_carrinho.preco is not None else 0 for produto_carrinho in produtos_carrinho)
            context = {
                'produtos': produtos,
                'total': total
            }
    elif not request.user.is_authenticated:
        carrinho = request.session.get('carrinho')
        print(carrinho)
        total= Decimal(0)
        produtos = []
        chaves = carrinho.keys()
        for chave in chaves:
            urlProdutoUP = f'http://127.0.0.1:8000/api/produtos_loja/{chave}/'
            resposta = requests.get(urlProdutoUP)
            
            
            
            produtoUP = resposta.json()
            nomeProduto = produtoUP['produto']['nome']
            quantidade = carrinho[chave]['quantidade']
            precoKilo = produtoUP['preco_a_granel'] if produtoUP['unidade_medida'] != 'un' else produtoUP['preco_por_unidade']
            preco = carrinho[chave]['precoQuantidade']
            total+=Decimal(preco)
            produtos.append({
                'produto' : produtoUP,
                'nomeProduto': nomeProduto,
                'quantidade':quantidade,
                'precoKilo':precoKilo,
                'preco':preco,
                'idNoCarrinho':chave
            })
        # carrinho = Carrinho.objects.get(consumidor=request.user.consumidor)
        # produtos_carrinho = carrinho.produtos_carrinho.all()
        #total_price = sum(produto_carrinho.preco if produto_carrinho.preco is not None else 0 for produto_carrinho in produtos_carrinho)
        context = {
            'produtos': produtos,
            'total': total
        }
    return render(request, 'loja/carrinho.html', context)

def adicionar_ao_carrinho(request, produto_id):
    """
    Adiciona um produto a um carrinho

    Args:
        request (_type_): request do browser
        produto_id (_type_): id de um ProdutoUnidadeProdução. NÃO É A FK da coluna produto na tabela ProdutoUnidadeProducao, 
                            é a coluna id. (produto = ProdutoUnidadeProducao.objects.get(id=produto_id)) 

    Returns:
        _type_: _description_
    """
    data = request.GET.get('preco')
    split_values = data.split('?')
    valor = Decimal(split_values[0])
    quantidade = Decimal(split_values[1].split('=')[1])
    preco_atualizado = Decimal(str(valor * quantidade))
    carrinho = request.session.get('carrinho', {})
    if request.user.is_authenticated and request.user.is_consumidor:
        data = request.GET.get('preco')
        split_values = data.split('?')
        valor = Decimal(split_values[0])
        quantidade = Decimal(split_values[1].split('=')[1])
        preco_atualizado = Decimal(str(valor * quantidade))

        url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/produtoUP/{produto_id}/'
    
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)

        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}

        resposta = sessao.get(url, headers=headers)
        if resposta.status_code == 200:
            content = resposta.json()
            idProdutoNoCarrinho = content.get('id')
            # idCarrinho = content.get('carrinho')
            produtoUnidadeProducao = content.get('produto')
            idProdutoUnidadeProducao = produtoUnidadeProducao.get('id')
            quantidade_updated = Decimal(content.get('quantidade')) + quantidade
            print("Quantidade antiga:", content.get('quantidade'))
            print("Quantidade update:", quantidade_updated)
            
            atualizar_carrinho_dict_info = {
                'produto': idProdutoUnidadeProducao,
                'quantidade' : quantidade_updated
            }
            # # print(atualizar_carrinho_dict_info)
            
            urlAtualizar = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/{idProdutoNoCarrinho}/'
            respostaUpdate = sessao.put(urlAtualizar, headers=headers, data = atualizar_carrinho_dict_info)
            
            print("VALORES ATUALIZADOS:", respostaUpdate.json())
        else:
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)

            csrf_token = get_token(request)
            headers = {'X-CSRFToken':csrf_token}
            
            
            
                        
            atualizar_carrinho_dict_info = {
                'produto': produto_id,
                'quantidade' : quantidade
            }
            
            
            urlAtualizar = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/'
            respostaUpdate = sessao.post(urlAtualizar, headers=headers, data = atualizar_carrinho_dict_info)
        
        # produto = ProdutoUnidadeProducao.objects.get(id=produto_id)
        # carrinho = Carrinho.objects.get(consumidor=request.user.consumidor)
        # produto_carrinho, created = ProdutosCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)

        # if created:
            
        #     produto_carrinho.quantidade = quantidade
        #     produto_carrinho.preco = preco_atualizado
        #     produto_carrinho.precoKilo = valor
        #     produto_carrinho.save()
        #     messages.success(request, 'O produto foi adicionado ao carrinho com sucesso.')
        # else:
        #     # O produto já está no carrinho, então atualize a quantidade e o preço
        #     produto_carrinho.quantidade += quantidade
        #     produto_carrinho.preco += preco_atualizado
        #     produto_carrinho.save()
        #     messages.success(request, 'O produto foi atualizado com sucesso.')
    elif request.user.is_authenticated and request.user.is_fornecedor:
        return redirect('loja-home')
    else:
        data = request.GET.get('preco')
        split_values = data.split('?')
        valor = float(split_values[0])
        quantidade = float(split_values[1].split('=')[1])
        preco_atualizado = valor * quantidade
        produto_id_nao_autent = str(produto_id)

        if produto_id_nao_autent in carrinho.keys():
            carrinho[produto_id_nao_autent]['quantidade'] += quantidade
            carrinho[produto_id_nao_autent]['precoQuantidade'] += preco_atualizado
        else:
            carrinho[produto_id_nao_autent] = { 
                    'quantidade': quantidade,
                    'precoQuantidade' : preco_atualizado
            }
        
        request.session['carrinho'] = carrinho
    return redirect('loja-ver_produtos')
    

from django.shortcuts import get_object_or_404, redirect
from .models import Carrinho, ProdutosCarrinho

def remover_do_carrinho(request, produto_id):
    if request.user.is_authenticated:
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)

        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}



        
        urlDelete = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/{produto_id}/'
        respostaDelete = sessao.delete(urlDelete, headers=headers)
        

        
        
        # carrinho = Carrinho.objects.get(consumidor=request.user.consumidor)
        # produto_carrinho = get_object_or_404(ProdutosCarrinho, carrinho=carrinho, id=produto_id)

        # # Reduz a quantidade do produto no carrinho
        # # if produto_carrinho.quantidade > 1:
        # #     produto_carrinho.quantidade -= 1
        # #     produto_carrinho.save()
        # # else:
        # produto_carrinho.delete()
        if respostaDelete.status_code == 204:
            messages.success(request, 'O produto foi removido do carrinho com sucesso.')
        elif respostaDelete.status_code == 404:
            mensagem_erro = respostaDelete.json().get('detail', 'Produto não encontrado no carrinho')
            messages.error(request, mensagem_erro)
        else:
            messages.error(request, "Algo correu mal ao remover o produto do carrinho")
    else:
        carrinho = request.session.get('carrinho')
        idProdutoStr = str(produto_id)
        if idProdutoStr in carrinho.keys():
            carrinho.pop(idProdutoStr)
            messages.success(request, 'O produto foi removido do carrinho com sucesso.')
            request.session['carrinho'] = carrinho
        else:
            mensagem_erro = respostaDelete.json().get('detail', 'Produto não encontrado no carrinho')
            messages.error(request, mensagem_erro)
            
    return redirect('loja-carrinho')

    
@fornecedor_required
def removerAssociaoProdutoUP(request, idUnidadeProducao, idProdutoUnidadeProducao):    
    if request.method == 'POST':
        url = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/produtos/{idProdutoUnidadeProducao}/'
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)
        
        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}
        
        resposta = sessao.delete(url, headers=headers)
        
        if resposta.status_code == 204:
            if resposta.text:
                conteudo = resposta.json()
                detial = conteudo.get('detail', 'Erro desconhecido ao apagar a associação')
                print(conteudo)
        else:
            print("Erro ao apagar associação")
    return redirect('loja-unidadeProducao', userName=request.user.username, id=idUnidadeProducao)



#@login_required(login_url='loja-login')
@fornecedor_required
def criarAssociacaoProdutoUP(request):
    formulario = ProdutoUnidadeProducaoForm(user=request.user)
    if request.method == 'POST':
        form = ProdutoUnidadeProducaoForm(request.POST, request.FILES,user=request.user)
        # try:
        if form.is_valid():
            imagem = form.cleaned_data['imagem_produto']
            print("\n\n",type(imagem),"\n\n")
            produto = form.cleaned_data['produto']
            unidade_producao = form.cleaned_data['unidade_producao']
            descricao = form.cleaned_data['descricao']
            stock = form.cleaned_data['stock']
            unidade_medida = form.cleaned_data['unidade_medida']
            preco_a_granel = form.cleaned_data['preco_a_granel']
            unidade_Medida_Por_Unidade = form.cleaned_data['unidade_Medida_Por_Unidade']
            quantidade_por_unidade = form.cleaned_data['quantidade_por_unidade']
            preco_por_unidade = form.cleaned_data['preco_por_unidade']
            data_producao = form.cleaned_data['data_producao']
            marca = form.cleaned_data['marca']
            
            produto_up_data= {
                "produto": produto.id,
                "unidade_producao":unidade_producao.id,
                "descricao": descricao,
                "stock": float(stock),
                "unidade_medida": unidade_medida,
                "preco_a_granel": float(preco_a_granel) if preco_a_granel is not None else None,
                "unidade_Medida_Por_Unidade": unidade_Medida_Por_Unidade,
                "quantidade_por_unidade": float(quantidade_por_unidade) if quantidade_por_unidade is not None else None,
                "preco_por_unidade": float(preco_por_unidade) if preco_por_unidade is not None else None,
                "data_producao": data_producao.isoformat() if isinstance(data_producao, date) else None,
                "marca":marca
            }
            
            
            
            url = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{unidade_producao.id}/produtos/'

            
            
            
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)
        
            csrf_token = get_token(request)
            headers = {'X-CSRFToken':csrf_token}
        
            resposta = sessao.post(url, headers=headers,data=produto_up_data, files={"imagem_produto":imagem})
            if resposta.status_code == 201:
                #messages.success(request, 'Produto criado com sucesso.')
                return redirect('loja-perfil', userName=request.user.username)
            else:
                if resposta.status_code == 400:
                    error_code = resposta.json().get('error_code')
                    if error_code == 'INTEGRITY_ERROR':
                        form.add_error('produto', f'Já existe este produto ({produto}) nesta unidade de produção ({unidade_producao}).')
                    else:
                        form.add_error('produto', f'Outro erro 400 BAD REQUEST: {resposta.json().get("detail")}')

        else:
            # Se o formulário não é válido, armazena os erros em cada campo do formulário
            #print("Erro de validação do formulário")
            context = {'formulario': form}
            return render(request, 'loja/criarAssociacaoProdutoUP.html', context)
    context = {'formulario': formulario}
    return render(request, 'loja/criarAssociacaoProdutoUP.html', context)



def adicionarProdutosCarrinhoDpsDeLogar(request):
    carrinhoSessao = request.session['carrinho']
    chavesProdutos = carrinhoSessao.keys()
    for idProduto in chavesProdutos:
        #{'1': {'quantidade': 2.0, 'precoQuantidade': 6.0}, 
        # '3': {'quantidade': 1.0, 'precoQuantidade': 4.98},
        # '7': {'quantidade': 1.0, 'precoQuantidade': 4.65}}
        informacao = carrinhoSessao[idProduto]
        quantidade = informacao['quantidade']
        
        print("CHEGUEI AQUI")
        url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/produtoUP/{idProduto}/'
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)

        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}
        resposta = sessao.get(url, headers=headers)
        if resposta.status_code == 200:
            content = resposta.json()
            idProdutoNoCarrinho = content.get('id')
            produtoUnidadeProducao = content.get('produto')
            idProdutoUnidadeProducao = produtoUnidadeProducao.get('id')
            quantidade_updated = Decimal(content.get('quantidade')) + Decimal(quantidade)
            
            atualizar_carrinho_dict_info = {
                'produto': idProdutoUnidadeProducao,
                'quantidade' : quantidade_updated
            }
            # # print(atualizar_carrinho_dict_info)
            
            url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/{idProdutoNoCarrinho}/'
            respostaUpdate = sessao.put(url, headers=headers, data = atualizar_carrinho_dict_info)
        else:
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)

            csrf_token = get_token(request)
            headers = {'X-CSRFToken':csrf_token}
            
            
            
                        
            atualizar_carrinho_dict_info = {
                'produto': idProduto,
                'quantidade' : quantidade
            }
            
            
            url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/'
            respostaUpdate = sessao.post(url, headers=headers, data = atualizar_carrinho_dict_info)
    request.session['carrinho'] = {}
