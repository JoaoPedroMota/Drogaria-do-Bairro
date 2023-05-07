from django.forms import ModelForm
from django import forms
from .models import Utilizador, Fornecedor, UnidadeProducao, Veiculo
from django.contrib.auth.forms import UserCreationForm

class UtilizadorFormulario(UserCreationForm):
    class Meta:
        model = Utilizador
        fields = ['first_name','last_name', 'username', 'email', 'password1', 'password2', 'pais','cidade','telemovel','tipo_utilizador','imagem_perfil']
        
        
        
class FornecedorFormulario(ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['descricao']
        
        
        
class EditarPerfil(ModelForm):
    class Meta:
        model = Utilizador
        fields = ['first_name', 'last_name', 'username','email', 'pais','cidade','telemovel','imagem_perfil',]
        
        
        
        
class criarUnidadeProducaoFormulario(ModelForm):
    class Meta:
        model= UnidadeProducao
        fields = ['nome', 'pais','cidade','morada', 'tipo_unidade']
        
class criarVeiculoFormulario(ModelForm):
    class Meta:
        model=Veiculo
        fields = ['nome', 'tipo_veiculo']

class editarVeiculoFormulario(ModelForm):
    class Meta:
        model=Veiculo
        fields = ['nome', 'estado_veiculo']

class editarUnidadeProducaoFormulario(ModelForm):
    class Meta:
        model=UnidadeProducao
        fields = ['nome', 'pais','cidade','morada', 'tipo_unidade']

class ConfirmacaoForm(forms.Form):
    nome_veiculo = forms.CharField()