from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Utilizador, Fornecedor, Consumidor, UnidadeProducao, Veiculo
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UtilizadorFormulario, FornecedorFormulario, EditarPerfil, criarUnidadeProducaoFormulario, criarVeiculoFormulario
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import ConfirmacaoForm


# Create your views here.
def loja(request):
    context = {}
    return render(request, 'loja/loja.html', context)
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


def shop(request):
    context = {}
    return render(request, 'loja/shop.html', context)

def loginUtilizador(request):
    pagina='login'
    if request.user.is_authenticated:
      
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
            utilizador.cidade = utilizador.cidade.upper()
            utilizador.nome = utilizador.first_name+' '+ utilizador.last_name
            utilizador.save()
            login(request,utilizador)
            if utilizador.tipo_utilizador == "C":
                consumidor = Consumidor.objects.create(utilizador=utilizador)
                return redirect('loja-home')
            else:
                return redirect('loja-form-forcedor')

            
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

def logutUtilizador(request):
    logout(request)
    return redirect('loja-home')



@login_required(login_url='loja-login')
def editarPerfil(request):
    pagina = 'editarPerfil'
    utilizador = request.user
    form = EditarPerfil(instance=utilizador)
    if request.method == 'POST':
        form = EditarPerfil(request.POST, request.FILES,instance = utilizador)
        #fields = []
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
def apagarConta(request,pk):
    utilizador = Utilizador.objects.get(pk=pk)
    
    if request.user != utilizador:
        return HttpResponse('Você não deveria estar aqui!')
    if request.method == 'POST':
        logout(request)
        utilizador.delete()
        return redirect('loja-home')
    context={'objeto':utilizador, 'pagina':'apagar-conta'}
    return render(request,'loja/delete.html', context)
        
        

@login_required(login_url='loja-login')
def perfil(request, userName):
    utilizadorPerfil = Utilizador.objects.get(username=userName)
    pagina = 'perfil'
    context={'pagina':pagina, 'utilizadorView': utilizadorPerfil}
    if utilizadorPerfil.is_fornecedor():
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
    if request.user.is_fornecedor():
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



def unidadeProducao(request, userName, id):
    context = {}
    utilizador = Utilizador.objects.get(username=userName)
    fornecedor = utilizador.fornecedor
    #fornecedor.unidades_producao.all()
    unidadeProducao = fornecedor.unidades_producao.get(pk=id)
    veiculos = unidadeProducao.veiculo_set.all()
    
    num_veiculos = veiculos.count()
    
    
    context={'veiculos':veiculos, 'num_veiculos':num_veiculos, 'unidadeProducao':unidadeProducao}
    return render(request, 'loja/unidadeProducao.html', context)




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
    if request.user.is_fornecedor():
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

