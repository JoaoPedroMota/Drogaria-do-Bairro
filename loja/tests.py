from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
#from .models import Utilizador, Fornecedor, Consumidor, UnidadeProducao, Veiculo
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
#from .forms import UtilizadorFormulario, FornecedorFormulario, EditarPerfil, criarUnidadeProducaoFormulario, criarVeiculoFormulario, editarVeiculoFormulario, editarUnidadeProducaoFormulario
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
#from .forms import ConfirmacaoForm
import requests
#from api.serializers import *
from django.db.models import QuerySetF

def unidadeProducao(request, userName, id):
    context = {}
    # utilizador = Utilizador.objects.get(username=userName)
    # fornecedor = utilizador.fornecedor
    # #fornecedor.unidades_producao.all()
    # unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    # veiculos = unidadeProducao.veiculo_set.all()
    
    # num_veiculos = veiculos.count()
    url = 'http://127.0.0.1:8000/api/fornecedores/'+str(id)+'/unidadesProducao/'
    #url = 'http://127.0.0.1:8000/api/utilizadores/'
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Process the data as needed
        #return data
    else:
        print('Error:', response.status_code)
        print('Response:', response.content)
        return None
    print("informaçao que fui buscar: ",data)              
    print(data[0]['id'])
    unidadeProducao = data[0]['id']

    url2 = 'http://127.0.0.1:8000/api/fornecedores/'+str(id)+'/unidadesProducao/'+str(unidadeProducao)+'/veiculos/'
    #path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/veiculos/', views.getVeiculos),
    response2 = requests.get(url2)
    if response2.status_code == 200:
        data2 = response2.json()
        # Process the data as needed
        #return data
    else:
        print('Error:', response2.status_code)
        print('Response:', response2.content)
        return None

    print("informaçao que fui buscar 2: ",data2)
    num_veiculos = len(data2)
    print("num_veiculos",num_veiculos)
    veiculos = data2
    print("veiculos",veiculos)

    # queryset = QuerySet(model=veiculos, query=None, using='default')
    # queryset._result_cache = veiculos
    # print("\nprint the QUERYSET ",queryset)

    #context={'veiculos':veiculos, 'num_veiculos':num_veiculos, 'unidadeProducao':unidadeProducao}
    #return render(request, 'loja/unidadeProducao.html', context)

get = "ola"
sandra = "sandra"
unidadeProducao(get, sandra, 2)