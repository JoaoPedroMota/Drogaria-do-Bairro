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
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from .forms import ConfirmacaoForm
import requests
from django.db.models import QuerySet
from django.contrib.auth.hashers import check_password
from loja.api.serializers import *
from .utils import fornecedor_required, consumidor_required
from datetime import datetime, timedelta
from django_countries import countries
import pytz
import requests
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from loja.api.serializers import UtilizadorSerializer

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def createCheckoutSession(request, idDetalhesEnvio):
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}

    url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/'
    response = sessao.get(url, headers=headers).json()

    line_items = []
    for produto in response:
        idProduto = produto['produto']['produto']

        url = f'http://127.0.0.1:8000/api/produtosID/{idProduto}/'
        response2 = sessao.get(url, headers=headers).json()

        produtoNome = response2['nome']
        encomendaPreco = int(float(produto['preco'])*100)

        item = {
            'price_data': {
                'currency' : 'eur',
                'unit_amount' : encomendaPreco  ,
                'product_data' : {
                    'name' : produtoNome,
                },
            },
            'quantity' : 1
        }

        line_items.append(item)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types = ['card'],
        line_items = line_items,
        mode = 'payment',
        success_url=f'http://127.0.0.1:8000/paymentSuccess/{idDetalhesEnvio}/',
        cancel_url = 'http://127.0.0.1:8000/paymentFailure/',
    )

    request.session['checkout_session_id'] = checkout_session.id

    return redirect(checkout_session.url, code=303)


def payment_success(request, idDetalhesEnvio):
    messages.success(request, "O pagamento foi efetuado com sucesso")
    return redirect('loja-criarEncomenda', idDetalhesEnvio=idDetalhesEnvio)

def payment_failure(request):
    messages.error(request, "Erro - Houve um problema ao efetuar o pagamento")
    return redirect('loja-carrinho')

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

def quantosProdutosNoCarrinho(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:

            consumidor = request.user.consumidor if hasattr(request.user, 'consumidor') else None
            fornecedor = request.user.fornecedor if hasattr(request.user, 'fornecedor') else None
            if consumidor is not None:
                sessao = requests.Session()
                sessao.cookies.update(request.COOKIES)
                url = f"http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/"
                resposta = sessao.get(url)
                if resposta.status_code == 404 or resposta.status_code == 400 or resposta.status_code==500:
                    return 0
                if resposta.content:
                    conteudo = resposta.json() if resposta.json() else 0
                else:
                    return 0
                return len(conteudo) if len(conteudo) != 0 else 0

            else:
                return 0 
        elif request.user.is_consumidor:
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)
            url = f"http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/"
            resposta = sessao.get(url)
            if resposta.status_code == 404 or resposta.status_code == 400 or resposta.status_code==500:
                return 0
            
            if resposta.content:
                conteudo = resposta.json() if resposta.json() else 0
            else:
                return 0
            return len(conteudo) if len(conteudo) != 0 else 0
        elif request.user.is_authenticated and request.user.is_fornecedor:
            return 0
    else:

        carrinho = request.session.get('carrinho') 
        if carrinho is not None:

            return len(carrinho)
        else:

            return 0

# Create your views here.
def loja(request):
    context = {}
    if request.user.is_authenticated and request.user.is_consumidor:
        if request.session.get('carrinho') is not None and request.session.get('carrinho') !={}:
            adicionarProdutosCarrinhoDpsDeLogar(request)
    elif request.user.is_authenticated and request.user.is_fornecedor:
        if request.session.get('carrinho') is not None and request.session.get('carrinho') !={}:
            request.session['carrinho'] = {}
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    if produtosCarrinho == -1:
        context={"produtosCarrinho":"E"}
    else:
        context={"produtosCarrinho":produtosCarrinho}
    return render(request, 'loja/loja.html', context)


def contacts(request):
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {"produtosCarrinho":produtosCarrinho}
    return render(request, 'loja/contacts.html', context)
def about(request):
    context = {}
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {"produtosCarrinho":produtosCarrinho}
    return render(request, 'loja/about.html', context)

def news(request):
    context = {}
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {"produtosCarrinho":produtosCarrinho}
    return render(request, 'loja/news.html', context)

def listaProdutosSemStock(request):

    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    url = f"http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/"
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}

    resposta = sessao.get(url)

    if resposta.content:
        content=resposta.json()

        listaProdutosSemStock = []

        #percorre a lista de produtos
        for item in content:

            produto = item['produto']
            stock = produto['stock'] 
            quantidadeNoCarrinho=item["quantidade"]

            if float(quantidadeNoCarrinho)>float(stock):
                listaProdutosSemStock.append((content.index(item),stock))
        return listaProdutosSemStock
    else:
        return ["Sem produtos no carrinho"]

# def create_order(request):
#     sessao = requests.Session()
#     sessao.cookies.update(request.COOKIES)
#     url = f"http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/"
#     csrf_token = get_token(request)
#     headers = {'X-CSRFToken':csrf_token}

#     resposta = sessao.post(url, headers)

#     if resposta.content:
#         content=resposta.json()

#         listaProdutosSemStock = []

#     consumidor = request.user.consumidor
#     encomenda = Encomenda.objects.create(
#         consumidor=consumidor,
#         estado='Em processamento',
#     )

#     valor_total = 0
#     for item in content:
#         produto = item['produto']

#     for item in cart_items.get('produtos_carrinho', []):
 
#         ProdutosEncomenda.objects.create(
#             encomenda=encomenda,
#             produtos=item.get('produto'),
#             quantidade=item.get('quantidade'),
#             preco=item.get('preco'),
#             precoKilo=item.get('precoKilo'),
#         )

#     valor_total = sum(item.get('preco', 0) for item in cart_items.get('produtos_carrinho', []))
#     encomenda.valor_total = valor_total
#     encomenda.save()

#     response = requests.delete(url)

#     if response.status_code != 204:
#         return Response({'message': 'Erro ao excluir carrinho de compras'}, status=status.HTTP_400_BAD_REQUEST)

#     return Response({'message': 'Order created successfully!'}, status=status.HTTP_201_CREATED)

@login_required(login_url='loja-login')
def checkout(request):
    consumidor = request.user.consumidor if hasattr(request.user, 'consumidor') else None
    if consumidor is None:
        return redirect('loja-home')
    
    if request.method == 'POST':

        lista=listaProdutosSemStock(request) 
        
        #Caso haja produtos sem stock     
        if len(lista)!=0:
            if "Sem produtos no carrinho" in lista:
                messages.error(request,"Erro - Ainda não tem produtos no carrinho")
            else:
                for produto in lista:
                    messages.error(request, 'Erro: O Item '+str(int(float(produto[0])+1))+' não tem stock suficiente para a quantidade pedida, o stock atual é '+produto[1])

            return redirect('loja-carrinho')
        
        #Caso todos os produtos tenham stock 
        else:
            return redirect('loja-confirmarDetalhesEnvio')
        
# def confirm_password_view(request):
#     if request.method == 'POST':
#         form = PasswordConfirmForm(request.POST)
#         if form.is_valid():
#             password = form.cleaned_data['password']
#             confirm_password = form.cleaned_data['confirm_password']
#             username = request.user.username
#             user = authenticate(username=username, password=password)

#             if user is not None:
#                 pass
#             else:
#                 # Password doesn't match, show an error message
#                 form.add_error('password', 'Incorrect password.')
#     else:
#         form = PasswordConfirmForm()
    
#     context = {'form': form}
#     return render(request, 'password_confirm.html', context)

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
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {'form':form, 'pagina':pagina, "produtosCarrinho":produtosCarrinho}
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
            utilizador.cidade = request.POST.get('cidade').upper()
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
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {'form':form, "produtosCarrinho":produtosCarrinho}
    return render(request, 'loja/completarPerfil.html', context)

@login_required(login_url='loja-login')
def apagarConta(request, pk):
    utilizador = Utilizador.objects.get(pk=pk)

    if request.user != utilizador:
        return redirect('loja-perfil', userName=request.user.username)

    if request.method == 'POST':
        username = request.POST.get('username')
        if username == request.user.username:
            logout(request)
            utilizador.delete()
            return redirect('loja-home')
        else:
            messages.error(request, 'Senha incorreta. A conta não foi excluída.')

    context = {'objeto': utilizador, 'pagina': 'apagar-conta'}
    return render(request, 'loja/delete.html', context)



# @login_required(login_url='loja-login')
# def apagarConta(request, pk):
#     utilizador = Utilizador.objects.get(pk=pk)

#     if request.user != utilizador:
#         return redirect('loja-perfil', userName=request.user.username)

#     if request.method == 'POST':
#         email = request.POST.get('email')
#         if email == utilizador.email:
#             logout(request)
#             utilizador.delete()
#             return redirect('loja-home')
#         else:
#             messages.error(request, 'Email incorreto. A conta não foi excluída.')
#             return redirect('loja-perfil', userName=request.user.username)

#     context = {'objeto': utilizador, 'pagina': 'apagar-conta'}
#     return render(request, 'loja/delete.html', context)

@login_required(login_url='loja-login')
def perfil(request, userName):
    utilizadorPerfil = Utilizador.objects.get(username=userName)
    pagina = 'perfil'
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context={'pagina':pagina, 'utilizadorView': utilizadorPerfil, "produtosCarrinho":produtosCarrinho}
    if request.user.username != userName:
        pass
    elif request.user.is_superuser:
        consumidor = utilizadorPerfil.consumidor if hasattr(utilizadorPerfil, 'consumidor') else None
        fornecedor = utilizadorPerfil.fornecedor if hasattr(utilizadorPerfil, 'fornecedor') else None
        if consumidor is not None:
            consumidor = utilizadorPerfil.consumidor
            url = f'http://127.0.0.1:8000/api/{utilizadorPerfil.username}/consumidor/encomenda/'
            
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)
            csrf_token = get_token(request)
            headers = {'X-CSRFToken':csrf_token}
            resposta = sessao.get(url, headers=headers)
            try:
                listaEncomendas = []
                todasEncomendas = resposta.json()
                for encomenda in todasEncomendas:
                    idEncomenda = encomenda['id']
                    valor_total = encomenda['valor_total']
                    detalhes_envio = encomenda['detalhes_envio']
                    
                    updated_temp = encomenda['updated']
                    updated = datetime.strptime(updated_temp, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(pytz.timezone('Europe/Lisbon'))
                    created_temp = encomenda['created']
                    created = datetime.strptime(created_temp, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(pytz.timezone('Europe/Lisbon'))
                    estado = encomenda['estado']
                    encomenda_dicio = {"idEncomenda":idEncomenda, "valor_total":valor_total, "detalhes_envio": detalhes_envio, "updated":updated, "created":created, "estado":estado}
                    listaEncomendas.append(encomenda_dicio)
                context['encomendas'] = listaEncomendas
                context['numero_encomendas'] = len(listaEncomendas)
            except json.decoder.JSONDecodeError:
                pass
        elif fornecedor is not None:
            fornecedor = utilizadorPerfil.fornecedor
            unidadesProducao = fornecedor.unidades_producao.all()
            numero_up = unidadesProducao.count()
            context['unidadesProducao'] = unidadesProducao
            context['numero_up'] = numero_up
        else:
            pass
    elif utilizadorPerfil.is_fornecedor:
        fornecedor = utilizadorPerfil.fornecedor
        unidadesProducao = fornecedor.unidades_producao.all()
        numero_up = unidadesProducao.count()
        context['unidadesProducao'] = unidadesProducao
        context['numero_up'] = numero_up
    elif utilizadorPerfil.is_consumidor:
        consumidor = utilizadorPerfil.consumidor
        
        
        
        
        url = f'http://127.0.0.1:8000/api/{utilizadorPerfil.username}/consumidor/encomenda/'
        
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)
        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}
        resposta = sessao.get(url, headers=headers)
        try:
            listaEncomendas = []
            todasEncomendas = resposta.json()
            for encomenda in todasEncomendas:
                idEncomenda = encomenda['id']
                valor_total = encomenda['valor_total']
                detalhes_envio = encomenda['detalhes_envio']
                
                updated_temp = encomenda['updated']
                updated = datetime.strptime(updated_temp, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(pytz.timezone('Europe/Lisbon'))
                created_temp = encomenda['created']
                created = datetime.strptime(created_temp, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(pytz.timezone('Europe/Lisbon'))
                estado = encomenda['estado']
                encomenda_dicio = {"idEncomenda":idEncomenda, "valor_total":valor_total, "detalhes_envio": detalhes_envio, "updated":updated, "created":created, "estado":estado}
                listaEncomendas.append(encomenda_dicio)
            context['encomendas'] = listaEncomendas
            context['numero_encomendas'] = len(listaEncomendas)
        except json.decoder.JSONDecodeError:
            pass
    else:
        context['outro'] = 'Outro'
    return render(request,'loja/perfil.html',context)

# @login_required(login_url='loja-login')
@fornecedor_required
def criarUP(request, userName):
    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor_id = utilizador.fornecedor
    pagina = 'criarUP'
    formulario = criarUnidadeProducaoFormulario()
    if request.user.is_fornecedor:
        if request.method == 'POST':
            formulario = criarUnidadeProducaoFormulario(request.POST)
            if formulario.is_valid():
                cidade_upper = request.POST.get('cidade')
                UnidadeProducao.objects.create(
                    fornecedor = fornecedor_id,
                    tipo_unidade = request.POST.get('tipo_unidade'),
                    nome = request.POST.get('nome'),
                    pais = request.POST.get('pais'),
                    cidade = cidade_upper.upper(),
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





@fornecedor_required
def unidadeProducao(request, userName, id):
    context = {}
    
    def criar_produto_temporario(produtosUPRespostaJSON):
        lista_produtos_up = []
        nome_up = ""
        semaforo = 0
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
            
            
            
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)
            
            urlFornecedor = f'http://127.0.0.1:8000/api/{usernameFornecedor}/fornecedor/'
            urlUtilizadorFornecedor = f'http://127.0.0.1:8000/api/{usernameFornecedor}/utilizadores/'
            
            
            respostaFornecedor = sessao.get(urlFornecedor)
            respostaUtilizador = sessao.get(urlUtilizadorFornecedor)
            
            dicionarioFornecedor = respostaFornecedor.json()
            dicionarioUtilizador = respostaUtilizador.json()
            #print(dicionarioUtilizador)
            
            
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

    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
    else:
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

        
        unidade_producao = UnidadeProducao.objects.get(id=id)
        ######produtos
        urlProdutosUP = f'http://127.0.0.1:8000/api/{userName}/fornecedor/unidadesProducao/{id}/produtos/'



        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)
        respostaProdutosUP = sessao.get(urlProdutosUP)
        if respostaProdutosUP.status_code != 404 and respostaProdutosUP.status_code != 500:
            produtosUP = respostaProdutosUP.json() 

            lista_produtos_up,nome_up = criar_produto_temporario(produtosUP)
        else:
        #-------------
            lista_produtos_up = []
            nome_up = unidade_producao.nome
        
        encomendas = ProdutosEncomenda.objects.filter(unidadeProducao=unidade_producao)

        
        dicionarioProdutosEstaoVeiculos = {}
        ###### produtos encomendados em veiculos de transporte
        for produto in encomendas:
            urlProdutosVeiculos = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{id}/produtoEncomendadoVeiculo/{produto.id}/'
            #print(urlProdutosVeiculos)
            sessao = requests.Session()
            sessao.cookies.update(request.COOKIES)
            csrf_token = get_token(request)
            headers = {'X-CSRFToken':csrf_token}
            resposta = sessao.get(urlProdutosVeiculos, headers=headers)
            # print(produto.id)
            if resposta.status_code == 404:
                dicionarioProdutosEstaoVeiculos[produto.id] = (False, None)
            else:
                conteudo = resposta.json()
                # print(conteudo)
                id_veiculo = conteudo[0]['veiculo']
                urlVeiculo = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{id}/veiculos/{id_veiculo}/'
                # print(urlVeiculo)
                resposta = sessao.get(urlVeiculo, headers=headers)
                nome_veiculo_conteudo = resposta.json()
                nome_mesmo = nome_veiculo_conteudo['nome']
                id_veiculo = nome_veiculo_conteudo['id']
                dicionarioProdutosEstaoVeiculos[produto.id] = (True, nome_mesmo, id_veiculo)
            

        context={'veiculos':veiculos, 'num_veiculos':num_veiculos, 'unidadeProducao':id, "produtosUP":lista_produtos_up, 'nome_up':nome_up,'encomenda':encomendas, "produtosEstaoEmVeiculos":dicionarioProdutosEstaoVeiculos}
        return render(request, 'loja/unidadeProducao.html', context)

#######################ZONA DE TESTE######################################################

# @login_required(login_url='loja-login')
@fornecedor_required
def editarUnidadeProducao(request, userName, id):
    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
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
                unidadeProducao.cidade = request.POST.get('cidade').upper()
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

@fornecedor_required
def removerUnidadeProducao(request, userName, id):
    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
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
    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
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
    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
    pagina = 'editarVeiculo'
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor= utilizador.fornecedor
    unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    veiculo = Veiculo.objects.get(pk=idVeiculo)
    formulario = editarVeiculoFormulario(instance=veiculo)
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
    if request.user.username != userName:
        return redirect('loja-perfil', userName=request.user.username)
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


# @login_required(login_url='loja-login')
@fornecedor_required
def criar_produto(request, userName):
    fornecedor = request.user.fornecedor if hasattr(request.user, 'fornecedor') else None
    
    if fornecedor is None:
        return redirect('loja-perfil', userName=request.user.username)
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
            csrf_token = get_token(request)
            headers = {'X-CSRFToken':csrf_token}
            
            
            resposta = sessao.post(urlCriarProduto, data=produto_data, headers=headers)
            if resposta.status_code == 201:
                messages.success(request, 'Produto criado com sucesso, já pode associar o produto criado a uma unidade de produção!')
                return redirect('loja-perfil', userName=request.user.username)
            else:
                #print("ERRO!!!!!!!!")
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

    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context={'filtered_products':filtered_products, "produtosCarrinho":produtosCarrinho}
    return render(request, 'loja/single-product.html',context)

def ver_produtos(request):
    q = request.GET.get('q', '')
    url1 = 'http://127.0.0.1:8000/api/produtos/'
    url2 = 'http://127.0.0.1:8000/api/produtos_loja/'
    response1 = requests.get(url1).json()
    response2 = requests.get(url2).json()

    response2_dict = {product['produto']: product for product in response2}

    merged_data = []
    for product1 in response1:
        product2 = response2_dict.get(product1['id'])
        if product2 is not None:
            merged_product = {
                'id': product1['id'],
                'nome': product1['nome'],
                'preco_a_granel': product2['preco_a_granel'],
                'preco_por_unidade': product2['preco_por_unidade'],
                'imagem_produto': product2['imagem_produto']
            }
            if 'categoria' in product1:
                merged_product['categoria'] = product1['categoria']['nome']
                merged_product['idCategoria'] = product1['categoria']['id']
            else:
                merged_product['categoria'] = None
                merged_product['idCategoria'] = None
            merged_data.append(merged_product)

    filtered_data = filter(
        lambda p: p['categoria'] is not None and
        (q.lower() in p['categoria'].lower() or q.lower() in p['nome'].lower()),
        merged_data
    )

    actualFilteredProducts = []
    for product in filtered_data:
        prices = []
        prices1 = []

        for shopProduct in response2:
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
                'categoria': product['categoria'],
                'idCategoria': product['idCategoria'],
            }
            lowest_price_product = next(
                (
                    shopProduct for shopProduct in response2
                    if shopProduct['produto'] == product['id'] and shopProduct['preco_a_granel'] == min_price
                ), None
            )
            if lowest_price_product is None:
                lowest_price_product = next(
                    (
                        shopProduct for shopProduct in response2
                        if shopProduct['produto'] == product['id'] and shopProduct['preco_por_unidade'] == min_price1
                    ), None
                )

            if lowest_price_product is not None:
                product_info['imagem_produto'] = lowest_price_product['imagem_produto']

            actualFilteredProducts.append(product_info)

    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {'produtos_precos': actualFilteredProducts, 'termo_pesquisa': q, "produtosCarrinho": produtosCarrinho}
    return render(request, 'loja/shop.html', context)


def carrinho(request):
    fornecedor = request.user.fornecedor if hasattr(request.user, 'fornecedor') else None
    if fornecedor is not None:
        return redirect('loja-home')
    # if request.session.get('carrinho') is not None and request.session.get('carrinho') != {}:
    #     print(request.session['carrinho'])
    context = {}
    if request.user.is_authenticated:
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)
        url = f"http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/"
        resposta = sessao.get(url)
        if resposta.content:
            try:
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
                produtosCarrinho = quantosProdutosNoCarrinho(request)
                context = {
                    'produtos': produtos,
                    'total': total,
                    "produtosCarrinho": produtosCarrinho
                }
            except json.decoder.JSONDecodeError:
                total= Decimal(0)
                #print("ENREI NO EXCEPT!")
                produtosCarrinho = quantosProdutosNoCarrinho(request)
                context= {
                    'total': total,
                    "produtosCarrinho": produtosCarrinho
                }
                # carrinho = Carrinho.objects.get(consumidor=request.user.consumidor)
            # conteudo = resposta.json()
            # total= Decimal(0)
            # produtos = []
            # for produto in conteudo:
            #     produtoUP = produto['produto']
            #     idParaReceberNome = produtoUP['produto']
            #     urlNomeProduto = f'http://127.0.0.1:8000/api/produtosID/{idParaReceberNome}/'
            #     resposta = sessao.get(urlNomeProduto)
            #     nome = resposta.json()
            #     nomeProduto = nome['nome']
            #     quantidade = produto['quantidade']

            #     precoKilo = produto['precoKilo']
            #     preco = produto['preco']
            #     idProdutoNoCarrinho = produto['id']
            #     total+=Decimal(preco)
            #     produtos.append({
            #         'produto' : produtoUP,
            #         'nomeProduto': nomeProduto,
            #         'quantidade':quantidade,
            #         'precoKilo':precoKilo,
            #         'preco':preco,
            #         'idNoCarrinho':idProdutoNoCarrinho
            #     })
            # # carrinho = Carrinho.objects.get(consumidor=request.user.consumidor)

            # produtos_carrinho = carrinho.produtos_carrinho.all()
            #total_price = sum(produto_carrinho.preco if produto_carrinho.preco is not None else 0 for produto_carrinho in produtos_carrinho)
        else:
            total= Decimal(0)
            #print("ENREI NO else!")
            produtosCarrinho = quantosProdutosNoCarrinho(request)
            context= {
                    'total': total,
                    "produtosCarrinho": produtosCarrinho
            }


    elif not request.user.is_authenticated:
        carrinho = request.session.get('carrinho')
        if carrinho is not None:
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
            produtosCarrinho = quantosProdutosNoCarrinho(request)
            context = {
                "produtosCarrinho": produtosCarrinho,
                'produtos': produtos,
                'total': total
            }
        else:
            total= Decimal(0)
            produtosCarrinho = quantosProdutosNoCarrinho(request)
            context = {
                "produtosCarrinho": produtosCarrinho,
                "total": total
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
    fornecedor = request.user.fornecedor if hasattr(request.user, 'fornecedor') else None
    if fornecedor is not None:
        return redirect('loja-home')
    # data = request.GET.get('preco')
    # split_values = data.split('?')
    # valor = Decimal(split_values[0])

    # quantidade = Decimal(split_values[1].split('=')[1])
    #print(request.GET)
    preco = Decimal(request.GET.get('preco'))
    quantidade = Decimal(request.GET.get('quantidade'))
    preco_atualizado = Decimal(preco * quantidade)
    
    carrinho = request.session.get('carrinho', {})
    if request.user.is_authenticated and request.user.is_consumidor:
        # data = request.GET.get('preco')
        # split_values = data.split('?')
        # valor = Decimal(split_values[0])
        #quantidade = Decimal(split_values[1].split('=')[1])
        #preco_atualizado = Decimal(str(valor * quantidade))
        preco = Decimal(request.GET.get('preco'))
        quantidade = Decimal(request.GET.get('quantidade'))
        preco_atualizado = Decimal(preco * quantidade)
        
        
        url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/produtoUP/{produto_id}/'
    
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)

        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}

        resposta = sessao.get(url, headers=headers)
        if resposta.status_code == 200: #ja existe o produto no carrinho, logo é um put
            content = resposta.json()
            idProdutoNoCarrinho = content.get('id')
            # idCarrinho = content.get('carrinho')
            produtoUnidadeProducao = content.get('produto')
            idProdutoUnidadeProducao = produtoUnidadeProducao.get('id')
            quantidadeTotal = Decimal(content.get('quantidade')) + quantidade
            if quantidadeTotal <= 999:
                quantidade_updated = Decimal(content.get('quantidade')) + quantidade
                atualizar_carrinho_dict_info = {
                    'produto': idProdutoUnidadeProducao,
                    'quantidade' : quantidade_updated
                }
                # # print(atualizar_carrinho_dict_info)
                
                urlAtualizar = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/carrinho/{idProdutoNoCarrinho}/'
                respostaUpdate = sessao.put(urlAtualizar, headers=headers, data = atualizar_carrinho_dict_info)
            else:
                mensagem_erro = "Erro: Quantidade máxima antigida. Máximo permitido é 999."
                messages.error(request, mensagem_erro)
            # print("VALORES ATUALIZADOS:", respostaUpdate.json())
        else: ### ainda não há o produto no carrinho logo é um post
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
        
        
        if True: #garbage. só para referencia futura
            pass
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
    elif request.user.is_authenticated and request.user.is_fornecedor: #é um fornecedor. não devia estar aqui. sai fora
        return redirect('loja-home')
    else: #utilizador não autenticado
        # data = request.GET.get('preco')
        # split_values = data.split('?')
        # valor = float(split_values[0])
        # quantidade = float(split_values[1].split('=')[1])
        preco = Decimal(request.GET.get('preco'))
        quantidade = Decimal(request.GET.get('quantidade'))
        # preco_atualizado = Decimal(preco * quantidade)
        
        preco_atualizado = preco * quantidade
        produto_id_nao_autent = str(produto_id)

        if produto_id_nao_autent in carrinho.keys():
            totalQuantidade = carrinho[produto_id]['quantidade'] + float(quantidade)
            if totalQuantidade <= 999:
                carrinho[produto_id_nao_autent]['quantidade'] += float(quantidade)
                carrinho[produto_id_nao_autent]['precoQuantidade'] += float(preco_atualizado)
            else:
                mensagem_erro = "Erro: Quantidade máxima antigida. Máximo permitido é 999."
                messages.error(request, mensagem_erro)
                
        else:
            carrinho[produto_id_nao_autent] = { 
                    'quantidade': float(quantidade),
                    'precoQuantidade' : float(preco_atualizado)
            }
        
        request.session['carrinho'] = carrinho
    return redirect('loja-ver-produtos')
    



def remover_do_carrinho(request, produto_id):
    fornecedor = request.user.fornecedor if hasattr(request.user, 'fornecedor') else None
    if fornecedor is not None:
        return redirect('loja-home')
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
def removerAssociaoProdutoUP(request, username, idUnidadeProducao, idProdutoUnidadeProducao):    
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
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
                #detail = conteudo.get('detail', 'Erro desconhecido ao apagar a associação')
                # print(conteudo)
        else:
            messages.error("Erro ao apagar associação")
    return redirect('loja-unidadeProducao', userName=request.user.username, id=idUnidadeProducao)



#@login_required(login_url='loja-login')
@fornecedor_required
def criarAssociacaoProdutoUP(request, username):
    formulario = ProdutoUnidadeProducaoForm(user=request.user)
    if request.method == 'POST':
        form = ProdutoUnidadeProducaoForm(request.POST, request.FILES,user=request.user)
        # try:
        if form.is_valid():
            imagem = form.cleaned_data['imagem_produto']
            # print("\n\n",type(imagem),"\n\n")
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
                messages.success(request, 'Produto associcado a unidade de produção com sucesso.')
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
        
        # print("CHEGUEI AQUI")
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



@consumidor_required
def confirmarDetalhesEnvio(request):
    consumidor = request.user.consumidor if hasattr(request.user, 'consumidor') else None
    if consumidor is None:
        return redirect('loja-home')
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {"produtosCarrinho":produtosCarrinho} # "produtosCarrinho":produtosCarrinho
    formulario = ConfirmarDetalhesEnvioForm(utilizador=request.user, validarNovosDetalhes=False)
    # print("123")
    
    
    url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/detalhes_envio/'

    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}

    resposta = sessao.get(url, headers=headers)
    # print("456")

    existe=False

    if resposta.content:
        # print("HA CONTENT") 
        conteudo = resposta.json()
        primeiro = next(iter(conteudo))
        existe=True
        formulario = ConfirmarDetalhesEnvioForm(utilizador=request.user, validarNovosDetalhes=True)

        formulario.initial = {
            'nome': primeiro['nome'],
            'pais': primeiro['pais'],
            'cidade': primeiro['cidade'],
            'morada': primeiro['morada'],
            'telemovel': primeiro['telemovel'],
            'email': primeiro['email'],
            'instrucoes_entrega': primeiro['instrucoes_entrega'],
            'usar_informacoes_utilizador': primeiro['usar_informacoes_utilizador'],
            'guardar_esta_morada': primeiro['guardar_esta_morada'],            
        }
      

    if request.method=="POST":
        if existe:
            #print("EXISTE = TRUE")
            validarNovosDetalhes=True
        else:
            #print("EXISTE = FALSE")
            validarNovosDetalhes=False

        formulario = ConfirmarDetalhesEnvioForm(request.POST, utilizador=request.user, validarNovosDetalhes=validarNovosDetalhes )
        
        dicionario_mutavel = formulario.data.copy()
        
        dicionario_mutavel['consumidor'] = request.user.consumidor
        dicionario_mutavel['cidade'] = formulario.data['cidade'].upper()
        #print(dicionario_mutavel)
        formulario.data = dicionario_mutavel
        #print("formulario.is_valid!!!:",formulario.is_valid())
        if formulario.is_valid():
            
            if True: ##esconder campos que vai buscar
                nome = formulario.cleaned_data["nome"]
                pais_temp = formulario.cleaned_data['pais']
                pais_long=countries.name(pais_temp)
                cidade = formulario.cleaned_data['cidade']
                morada = formulario.cleaned_data['morada']
                ### campo telemovel
                telemovel = formulario.cleaned_data['telemovel']
                ####converter telemovel para formato internacional
                international_phone_number = phonenumbers.format_number(telemovel, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                ### converte para str
                telemovel_international_str = str(international_phone_number)
                #### atribui str ao dicionario, pq JSON  n suporta PhoneNumber
                instrucoes_entrega=formulario.cleaned_data['instrucoes_entrega']
                
                
                telemovel = telemovel_international_str
                email = formulario.cleaned_data['email']
                guardar_esta_morada = formulario.cleaned_data['guardar_esta_morada']

                # print(guardar_esta_morada, type(guardar_esta_morada))

            if resposta.status_code == 200 and guardar_esta_morada == True: ##ja existem detalhes criados para este user

                
                conteudo=resposta.json()
                primeiro = next(iter(conteudo))

                
                #verificar se ha alguma alteracao
                if primeiro['nome'] != nome or primeiro['pais'] != pais_long or primeiro['cidade'] != cidade or primeiro['telemovel'] != telemovel or primeiro['email'] != email or primeiro['morada'] != morada or primeiro['instrucoes_entrega'] != instrucoes_entrega:
                    # print("ENTROU NO IF")
                    detalhes_entrega={
                        "nome":nome,
                        "pais":pais_long,
                        "cidade":cidade,
                        "telemovel":telemovel,
                        "morada":morada,
                        "email" : email,
                        "instrucoes_entrega" : instrucoes_entrega,
                        "guardar_esta_morada" : guardar_esta_morada,
                    }

                    if guardar_esta_morada:
                        idDetalhesEnvio= primeiro['id']

                        url += f"{idDetalhesEnvio}/"
                        resposta = sessao.put(url, headers=headers, data=detalhes_entrega)

                        if resposta.status_code == 200: #correu tudo bem?
                            messages.success(request, "Detalhes de envio guardados com sucesso")
                            #return redirect('loja-perfil', userName=request.user.username)  #FALTA VER
                            return redirect('loja-checkoutSession', idDetalhesEnvio=idDetalhesEnvio)
                        else: #deu erro
                            formulario.add_error('nome',f'Erro: {resposta}')
                    # else:

                    #     resposta = sessao.post(url, headers=headers, data=detalhes_entrega)

                    #     conteudo=resposta.json()
                    #     primeiro = next(iter(conteudo))
                    #     idDetalhesEnvio= primeiro['id']

                    #     if resposta.status_code == 201: #correu tudo bem?
                    #         messages.success(request, "Detalhes de envio guardados com sucesso")
                    #         return redirect('loja-perfil', userName=request.user.username)  #FALTA VER
                    #     else: #deu erro
                    #         formulario.add_error('nome',f'Erro: {resposta}')
                else:

                    # print("Resposta da API:", resposta.json())
                    # print("PRIMEIRO!!!",primeiro)
                    # print("CONTEUDO!!!",conteudo)
                    idDetalhesEnvio= primeiro['id']

            elif resposta.status_code == 200 and guardar_esta_morada == False:#ja existem detalhes mas nao quero guardar no perfil os novos detalhes
                
                conteudo=resposta.json()
                primeiro = next(iter(conteudo))

                # if primeiro['nome'] != nome or primeiro['pais'] != pais_long or primeiro['cidade'] != cidade or primeiro['telemovel'] != telemovel or primeiro['email'] != email or primeiro['morada'] != morada or primeiro['instrucoes_entrega'] != instrucoes_entrega:

                detalhes_entrega={
                    "nome":nome,
                    "pais":pais_long,
                    "cidade":cidade,
                    "telemovel":telemovel,
                    "morada":morada,
                    "email" : email,
                    "instrucoes_entrega" : instrucoes_entrega,
                    "guardar_esta_morada" : guardar_esta_morada,
                }

                    # if guardar_esta_morada:
                    #     idDetalhesEnvio= primeiro['id']

                    #     url += f"{idDetalhesEnvio}/"
                    #     resposta = sessao.put(url, headers=headers, data=detalhes_entrega)

                    #     if resposta.status_code == 200: #correu tudo bem?
                    #         messages.success(request, "Detalhes de envio guardados com sucesso")
                    #         return redirect('loja-perfil', userName=request.user.username)  #FALTA VER
                    #     else: #deu erro
                    #         formulario.add_error('nome',f'Erro: {resposta}')
                    # else:

                resposta = sessao.post(url, headers=headers, data=detalhes_entrega)

                conteudo=resposta.json()
                primeiro = next(iter(conteudo))
                # print("PRIMEIRO!!!",primeiro)
                # print("CONTEUDO!!!",conteudo)
                idDetalhesEnvio= conteudo["id"]

                if resposta.status_code == 201: #correu tudo bem?
                    messages.success(request, "Detalhes de envio guardados com sucesso para esta encomenda")
                    #return redirect('loja-criarEncomenda', userName=request.user.username)
                    return redirect('loja-checkoutSession', idDetalhesEnvio=idDetalhesEnvio)
                else: #deu erro
                    formulario.add_error('nome',f'Erro: {resposta}')

            else: #ainda não existe detalhes de envio
                detalhes_entrega={
                    "nome":nome,
                    "pais":pais_long,
                    "cidade":cidade.upper(),
                    "telemovel":telemovel,
                    "morada":morada,
                    "email" : email,
                    "instrucoes_entrega" : instrucoes_entrega,
                    "guardar_esta_morada":guardar_esta_morada
                }
                # print(detalhes_entrega["nome"])
                # print(detalhes_entrega["pais"])
                # print(detalhes_entrega["cidade"])
                # print(detalhes_entrega["telemovel"])
                # print(detalhes_entrega["morada"])
                # print(detalhes_entrega["email"])
                # print(detalhes_entrega["instrucoes_entrega"])
                # print(detalhes_entrega["guardar_esta_morada"])
                resposta = sessao.post(url, headers=headers, data=detalhes_entrega)
                # print(resposta)
                # print(resposta.json())
                if resposta.status_code == 201:
                    conteudo=resposta.json()
                    idDetalhesEnvio=conteudo['id']
                    messages.success(request, "Detalhes de envio guardados com sucesso")
                    #return redirect('loja-perfil', userName=request.user.username)
                    return redirect('loja-checkoutSession', idDetalhesEnvio=idDetalhesEnvio)
                else:
                    #("FORMULARIO ERRORS", formulario.errors)
                    formulario.add_error('nome', f'Erro:{resposta}')
        else:
            context = {'formulario': formulario}
            return render(request, 'loja/confirmarDetalhesEnvio.html', context)   
    context['formulario'] = formulario
    return render(request, 'loja/confirmarDetalhesEnvio.html', context)

# except json.decoder.JSONDecodeError:
    

@consumidor_required
def criarEncomenda(request, idDetalhesEnvio):
    consumidor = request.user.consumidor if hasattr(request.user, 'consumidor') else None
    if consumidor is None:
        return redirect('loja-home')

    url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/encomendarCarrinho/'
    #print("CHEGUEI A CRIAR ENCOMENDAS")
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}

    idCheckoutSession = request.session.get('checkout_session_id')

    data={'detalhes_envio': idDetalhesEnvio, 'idCheckoutSession' : idCheckoutSession}

    resposta = sessao.post(url, data=data,headers=headers)
    if resposta.status_code == 201:
        messages.success(request, "A sua encomenda foi criada com sucesso")
        return redirect('loja-perfil', userName=request.user.username)
    else:
        messages.error(request, "Erro - Houve um problema a criar a sua encomenda")
        return redirect('loja-carrinho')


@consumidor_required
def detalhesEnvio(request, username):
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    context = {"produtosCarrinho":produtosCarrinho} # "produtosCarrinho":produtosCarrinho
    formulario = DetalhesEnvioForm(utilizador=request.user)
    url = f'http://127.0.0.1:8000/api/{request.user.username}/consumidor/detalhes_envio/'

    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}

    resposta = sessao.get(url, headers=headers)

    if resposta.content:
        conteudo = resposta.json()
        primeiro = next(iter(conteudo))
        formulario.initial = {
            'nome': primeiro['nome'],
            'pais': primeiro['pais'],
            'cidade': primeiro['cidade'],
            'morada': primeiro['morada'],
            'telemovel': primeiro['telemovel'],
            'email': primeiro['email'],
            'instrucoes_entrega': primeiro['instrucoes_entrega'],
            'usar_informacoes_utilizador': primeiro['usar_informacoes_utilizador'],
            'guardar_esta_morada': primeiro['guardar_esta_morada']
        }

    if request.method=="POST":
        formulario = DetalhesEnvioForm(request.POST, utilizador=request.user)
        
        dicionario_mutavel = formulario.data.copy()
        
        dicionario_mutavel['consumidor'] = request.user.consumidor
        dicionario_mutavel['cidade'] = formulario.data['cidade'].upper()
        #print(dicionario_mutavel)
        formulario.data = dicionario_mutavel
        if formulario.is_valid():
            
            if True: ##esconder campos que vai buscar
                nome = formulario.cleaned_data["nome"]
                pais_temp = formulario.cleaned_data['pais']
                if type(pais_temp) == type('ola'):
                    pais = pais_temp
                else:
                    pais = pais_temp.name
                cidade = formulario.cleaned_data['cidade']
                morada = formulario.cleaned_data['morada']
                
                ### campo telemovel
                telemovel = formulario.cleaned_data['telemovel']
                ####converter telemovel para formato internacional
                international_phone_number = phonenumbers.format_number(telemovel, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                ### converte para str
                telemovel_international_str = str(international_phone_number)
                #### atribui str ao dicionario, pq JSON  n suporta PhoneNumber
                
                
                
                telemovel = telemovel_international_str
                email = formulario.cleaned_data['email']
                instrucoes_entrega = formulario.cleaned_data['instrucoes_entrega']
                usar_informacoes_utilizador = formulario.cleaned_data['usar_informacoes_utilizador']
                guardar_esta_morada = formulario.cleaned_data['guardar_esta_morada']

            if resposta.status_code == 200: ##houve resposta
                

                detalhes_entrega={
                    "nome":nome,
                    "pais":pais,
                    "cidade":cidade,
                    "telemovel":telemovel,
                    "morada":morada,
                    "email" : email,
                    "instrucoes_entrega": instrucoes_entrega,
                    "guardar_esta_morada":guardar_esta_morada,
                    "usar_informacoes_utilizador": usar_informacoes_utilizador
                }
                
                ### pedido
                url += f"{primeiro['id']}/"
                resposta = sessao.put(url, headers=headers, data=detalhes_entrega)
                
                
                
                if resposta.status_code == 200: #correu tudo bem?
                    return redirect('loja-perfil', userName=request.user.username)
                else: #deu erro
                    formulario.add_error('nome',f'Erro: {resposta}')
                    
            else: #ainda não existe detalhes de envio
                detalhes_entrega={
                    "nome":nome,
                    "pais":pais,
                    "cidade":cidade.upper(),
                    "telemovel":telemovel,
                    "morada":morada,
                    "email" : email,
                    "instrucoes_entrega": instrucoes_entrega,
                    "usar_informacoes_utilizador": usar_informacoes_utilizador,
                    "guardar_esta_morada":guardar_esta_morada
                }
                resposta = sessao.post(url, headers=headers, data=detalhes_entrega)
                if resposta.status_code == 201:
                    return redirect('loja-perfil', userName=request.user.username)
                else:
                    formulario.add_error('nome', f'Erro:{resposta}')
        else:
            context = {'formulario': formulario}
            return render(request, 'loja/detalhesEnvio.html', context)   
    context['formulario'] = formulario
    return render(request, 'loja/detalhesEnvio.html', context)

@consumidor_required
def getProdutosEncomenda(request, username, idEncomenda):
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    produtosCarrinho = quantosProdutosNoCarrinho(request)
    url = f'http://127.0.0.1:8000/api/{username}/consumidor/encomenda/{idEncomenda}/produtos/'
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.get(url, headers=headers)
    context = {"produtosCarrinho":produtosCarrinho}
    totalEncomenda = Decimal(0)
    try:
        listaProdutosInEncomendas = []
        todosProdutos = resposta.json()
        for produto in todosProdutos:
            produto_up = produto['produtos']
            url = f'http://127.0.0.1:8000/api/produtos_loja/{produto_up}/'
            resposta_2 = requests.get(url)
            
            preco = produto['preco']
            precoKilo = produto['precoKilo']
            updated_temp = produto['updated']
            updated = datetime.strptime(updated_temp, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(pytz.timezone('Europe/Lisbon'))
            totalEncomenda += Decimal(preco)
            estado = produto['estado']
            idProdutoEncomendado = produto['id']
            idEncomenda = idEncomenda
            try:
                conteudo = resposta_2.json()
                infoProduto = conteudo['produto']
                nome_produto = infoProduto['nome']
                imagem_produto = conteudo['imagem_produto']
                unidade_medida = conteudo['unidade_medida']
                preco_a_granel = True if conteudo['preco_a_granel'] is not None else False
                if not preco_a_granel:
                    quantidade_temp = Decimal(produto['quantidade'])
                    quantidade = int(quantidade_temp)
                else:
                    quantidade = produto['quantidade']
                
                
                unidadeProducaoInfo = conteudo['unidade_producao']
                nome_up = unidadeProducaoInfo['nome']
                fornecedorInfo = unidadeProducaoInfo['fornecedor']
                fornecedor_nome = fornecedorInfo['utilizador']
            except json.decoder.JSONDecodeError:
                pass
                
                
            encomenda_dicio = {"idEncomenda":idEncomenda, "idProdutoEncomendado":idProdutoEncomendado,"imagem_produto":imagem_produto,"nome_produto":nome_produto, "precoKilo":precoKilo, "unidade_medida":unidade_medida,"preco_a_granel":preco_a_granel ,"preco":preco, "quantidade":quantidade, "estado":estado, "updated":updated, "nome_up":nome_up, "fornecedor_nome":fornecedor_nome}
            listaProdutosInEncomendas.append(encomenda_dicio)
        context['produtos_encomendados'] = listaProdutosInEncomendas
        context['numero_produtos'] = len(listaProdutosInEncomendas)
        context['total'] = totalEncomenda
    except json.decoder.JSONDecodeError:
        pass
    return render(request, 'loja/produtos_encomendados.html', context)

@consumidor_required
def cancelarProdutoEncomendado(request, username, idEncomenda, idProdutoEncomendado, nomeProduto):
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    
    
    if request.method == 'POST':
        url = f'http://127.0.0.1:8000/api/{username}/consumidor/encomenda/{idEncomenda}/produtos/{idProdutoEncomendado}/cancelar/'
        sessao = requests.Session()
        sessao.cookies.update(request.COOKIES)
        csrf_token = get_token(request)
        headers = {'X-CSRFToken':csrf_token}
        resposta = sessao.get(url, headers=headers)
        try:
            conteudo = resposta.json()
            estado = conteudo['estado']
            criado_temp = conteudo['created']
            if estado == "Em processamento":
                criado = datetime.strptime(criado_temp, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(pytz.timezone('Europe/Lisbon'))
                prazo_cancelamento = timedelta(hours=3)
                tempo_decorrido_desde_encomenda = timezone.now() - criado
                #print(tempo_decorrido_desde_encomenda, "tempo_decorrido_desde_encomenda")
                if tempo_decorrido_desde_encomenda < prazo_cancelamento:
                    resposta = sessao.put(url, headers=headers)

                    if resposta.status_code == 200:
                        url2 = f'http://127.0.0.1:8000/api/{username}/consumidor/encomenda/'
                        encomendas = sessao.get(url2, headers=headers).json()

                        for encomenda in encomendas:
                            if encomenda['id'] == idEncomenda:
                                idCheckoutSession = encomenda['idCheckoutSession']

                        checkout_session = stripe.checkout.Session.retrieve(idCheckoutSession)
                        payment_intent = checkout_session['payment_intent']

                        stripe.Refund.create(
                            payment_intent=payment_intent,
                            amount=int(float(conteudo['preco']))*100,
                        )
                        messages.success(request,f"O produto encomendado ({nomeProduto}), foi cancelado com sucesso e o reembolso foi efetuado")
                        return redirect('loja-perfil', userName=request.user.username)
                    else:
                        messages.error(request,"Houve um erro a cancelar o seu produto")
                        return redirect('loja-produtosEncomendados', idEncomenda=idEncomenda, username=username)
                else:
                    messages.error(request,f"Só pode cancelar encomendas até 3h depois de as realizar. Tempo decorrido desde a criação da encomenda: {tempo_decorrido_desde_encomenda}")
                    return redirect('loja-produtosEncomendados', idEncomenda=idEncomenda, username=username)
            elif estado == "Enviado" or estado == "Entregue" or estado == "A chegar":
                messages.error(request, f"A encomenda já está no estado {estado}. Já não pode cancelar nesta altura.")
                return redirect('loja-perfil', userName=request.user.username)
            elif estado == "Cancelado":
                messages.error(request, "Erro. A encomenda já foi cancelada")
                return redirect('loja-perfil', userName=request.user.username)
        except json.decoder.JSONDecodeError:
            messages.error(request,"Erro a cancelar encomenda. Tente novamente mais tarde.")
            return redirect('loja-perfil', userName=request.user.username)
        return redirect('loja-perfil', userName=request.user.username)

@consumidor_required
def verDetalhesEnvioNaEncomenda(request, username, idDetalhes, idEncomenda):
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    idDetalhes = int(idDetalhes)
    url = f'http://127.0.0.1:8000/api/{username}/consumidor/detalhes_envio/{idDetalhes}'
    url2 = f'http://127.0.0.1:8000/api/{username}/consumidor/encomenda/'
    
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.get(url, headers=headers)
    resposta_2 = sessao.get(url2, headers=headers)
    context = {} 
    try:
        conteudo = resposta.json()
        nome = conteudo['nome']
        morada = f"{conteudo['morada']}, {conteudo['cidade']}, {conteudo['pais']}"
        telemovel = conteudo['telemovel']
        email = conteudo['email']
        instrucoes_entrega = conteudo['instrucoes_entrega']
        ####################
        conteudo_2 = resposta_2.json()
        encomenda_dicio = {}
        for encomenda in conteudo_2:
            if encomenda['id'] == idEncomenda:
                encomenda_dicio = encomenda
                break
        index_encomenda = conteudo_2.index(encomenda_dicio)
        index_encomenda+=1
        
        
        info_detalhes_envio = [{"nome":nome, "morada":morada, "telemovel":telemovel, "email":email, "instrucoes_entrega":instrucoes_entrega}]
    except json.decoder.JSONDecodeError:
        pass
    context = {"infos":info_detalhes_envio, "encomenda_nr":index_encomenda}
    return render(request, 'loja/infos_detalhes.html', context)



@fornecedor_required
def getDetalhesParaFornecedor(request,username, idEncomenda, idUnidadeProducao):
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    
    url = f'http://127.0.0.1:8000/api/{username}/fornecedor/encomenda/{idEncomenda}/detalhes_envio/'
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.get(url, headers=headers)
    try:
        conteudo = resposta.json()
        nome = conteudo['nome']
        morada = f"{conteudo['morada']}, {conteudo['cidade']}, {conteudo['pais']}"
        telemovel = conteudo['telemovel']
        email = conteudo['email']
        instrucoes_entrega = conteudo['instrucoes_entrega']
        
        info_detalhes_envio = [{"nome":nome, "morada":morada, "telemovel":telemovel, "email":email, "instrucoes_entrega":instrucoes_entrega}]
        context = {"infos":info_detalhes_envio}
        return render(request, 'loja/infos_detalhes.html', context)
    except json.decoder.JSONDecodeError:
        messages.error(request, "Houve um erro a obter os detaalhes de envio do utilizador")
        return redirect('loja-unidadeProducao', username=request.user.username, id=idUnidadeProducao)



@fornecedor_required
def colocarProdutoEmVeiculoTransporte(request, username, idUnidadeProducao, idProdutoEncomenda):
    
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    
    
    formulario = ProdutosEncomendadosVeiculosForm(idUnidadeProducao=idUnidadeProducao)
    url = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/veiculosDisponiveis/'
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.get(url, headers=headers)
    if resposta.status_code == 200:
        if request.method == 'POST':
            formulario = ProdutosEncomendadosVeiculosForm(request.POST, idUnidadeProducao=idUnidadeProducao)
            # dicionario_mutavel = formulario.data.copy()
            # print(type(dicionario_mutavel['veiculo']))
            # print(dicionario_mutavel['veiculo'])
            if formulario.is_valid():
                veiculo = formulario.cleaned_data['veiculo']
                idVeiculo = veiculo.id
                data_enviar = {
                    "produto_Encomendado": idProdutoEncomenda
                }
                url2 = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/veiculos/{idVeiculo}/carregar/'
                resposta = sessao.post(url2, headers=headers, data=data_enviar)
                if resposta.status_code == 201:
                    messages.error(request, f"Encomenda colocado no veículo com sucesso!")
                    return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
                else:
                    # print(resposta.content)
                    messages.error(request, f"Algo correu mal ao colocar o produto no veículo")
                    return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
            
        context={"formulario":formulario}
        return render(request, 'loja/colocarEncomendaEmVeiculo.html', context)
    if resposta.status_code != 200 and request.method == 'GET':
        messages.error(request, f"Não tem veículos disponíveis de momento para colocar este produto.")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)


# form = ProdutoUnidadeProducaoForm(request.POST, request.FILES,user=request.user)
@fornecedor_required
def veiculoSairParaEntrega(request, username, idVeiculo, idUnidadeProducao):
    
    if request.user.username != username:
        return redirect("loja-perfil", userName=request.user.username)
    
    
    
    url = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/veiculos/{idVeiculo}/sair/'
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.put(url, headers=headers)
    if resposta.status_code == 200:
        messages.success(request, "Veiculo saiu para entregar encomendas!")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
    elif resposta.status_code == 404:
        messages.error(request, "Erro - O veículo não tem produtos carregados!")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
    elif resposta.status_code==400:
        mensagem_erro = resposta.json()['details']
        messages.error(request, f"Erro - {mensagem_erro}")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
        


@fornecedor_required
def entregarEncomenda(request, username, idUnidadeProducao,idVeiculo):
    if request.user.username != username:
        return redirect('loja-perfil', userName= request.user.username)
    
    
    url = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/veiculos/{idVeiculo}/entregar/'
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.put(url, headers=headers)
    if resposta.status_code == 200:
        messages.success(request, "Encomenda entregue e finalizada!")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
    elif resposta.status_code == 404:
        messages.error(request, "Veiculo não tem encomendas para entregar")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
    
    
@fornecedor_required
def veiculoRegressou(request, username, idUnidadeProducao, idVeiculo):
    if request.user.username != username:
        return redirect('loja-perfil', userName=request.user.username)
    
    url = f'http://127.0.0.1:8000/api/{username}/fornecedor/unidadesProducao/{idUnidadeProducao}/veiculos/{idVeiculo}/regressou/'
    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}
    resposta = sessao.put(url, headers=headers)
    if resposta.status_code == 200:
        conteudo = resposta.json()
        mensagem = conteudo['message']
        print(mensagem)
        messages.success(request, f"{mensagem}")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
    elif resposta.status_code == 400:
        conteudo = resposta.json()
        mensagem = conteudo['message']
        print(mensagem)
        messages.error(request, f"{mensagem}")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)
    else:
        messages.error("Houve algum erro ao realizar esta ação. Ou o veículo não existe ou acedeu a esta função fora de tempo")
        return redirect('loja-unidadeProducao', userName=username, id=idUnidadeProducao)


def editarAssociacaoProdutoUP(request, idUnidadeProducao, idProdutoUnidadeProducao):
    form = editarProdutoUnidadeProducaoForm(user=request.user)

    sessao = requests.Session()
    sessao.cookies.update(request.COOKIES)
    
    csrf_token = get_token(request)
    headers = {'X-CSRFToken':csrf_token}

    url = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/produtos/{idProdutoUnidadeProducao}/'
    response = sessao.get(url, headers=headers)

    if request.method == 'POST':
        form = editarProdutoUnidadeProducaoForm(request.POST, request.FILES,user=request.user)
        if form.is_valid():
            imagem = form.cleaned_data['imagem_produto']
            descricao = form.cleaned_data['descricao']
            stock = form.cleaned_data['stock']
            unidade_medida = form.cleaned_data['unidade_medida']
            preco_a_granel = form.cleaned_data['preco_a_granel']
            unidade_Medida_Por_Unidade = form.cleaned_data['unidade_Medida_Por_Unidade']
            quantidade_por_unidade = form.cleaned_data['quantidade_por_unidade']
            preco_por_unidade = form.cleaned_data['preco_por_unidade']
            data_producao = form.cleaned_data['data_producao']
            marca = form.cleaned_data['marca']

            
            
            produto_up_data = {
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
            
            if imagem:
                resposta = sessao.put(url, headers=headers,data=produto_up_data, files={"imagem_produto":imagem})
            else:
                resposta = sessao.put(url, headers=headers,data=produto_up_data)

            

            if resposta.status_code == 200:
                #messages.success(request, 'Produto criado com sucesso.')
                return redirect('loja-perfil', userName=request.user.username)
            else:
                if resposta.status_code == 400:
                    error_code = resposta.json().get('error_code')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}_error::{error}')
    
    try:
        content = response.json()
        form.initial = {
            'produto': content['produto'],
            'unidade_producao': content['unidade_producao'],
            'stock': content['stock'],
            'descricao': content['descricao'],
            'unidade_medida': content['unidade_medida'],
            'preco_a_granel': content['preco_a_granel'],
            'unidade_Medida_Por_Unidade': content['unidade_Medida_Por_Unidade'],
            'quantidade_por_unidade': content['quantidade_por_unidade'],
            'preco_por_unidade': content['preco_por_unidade'],
            'data_producao': content['data_producao'],         
            'marca': content['marca'],                          
        }
    except json.decoder.JSONDecodeError:
        pass
    
    url_up = f'http://127.0.0.1:8000/api/{request.user.username}/fornecedor/unidadesProducao/{idUnidadeProducao}/'
    response_up = sessao.get(url_up, headers=headers).json()

    idProduto = content['produto']
    url_produto = f'http://127.0.0.1:8000/api/produtosID/{idProduto}/'
    response_produto = sessao.get(url_produto, headers=headers).json()

    context = {'formulario': form, 'produto': response_produto, 'unidade_producao': response_up}
    return render(request, 'loja/editarAssociacaoProdutoUP.html', context)