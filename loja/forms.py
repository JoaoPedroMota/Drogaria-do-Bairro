from django.forms import ModelForm
from django import forms
from .models import Utilizador, Fornecedor, UnidadeProducao,Categoria , Veiculo, Produto, ProdutoUnidadeProducao
from django.contrib.auth.forms import UserCreationForm
from django import forms
class UtilizadorFormulario(UserCreationForm):
    class Meta:
        model = Utilizador
        fields = ['first_name','last_name', 'username', 'email', 'password1', 'password2', 'pais','cidade','telemovel','tipo_utilizador','imagem_perfil']
  
class FornecedorFormulario(ModelForm):

    pass
    # class Meta:
    #     model = Fornecedor
    #     fields = ['descricao']
                
        
        
        
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

class ConfirmacaoForm(forms.Form):
    nome_veiculo = forms.CharField()

class PasswordConfirmForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome']

class ProdutoUnidadeProducaoForm(forms.ModelForm):
    data_producao = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all())
    #categoria = forms.CharField(max_length=100, required=True)
    #marca = forms.CharField(max_length=50)
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ['produto', 'unidade_producao', 'descricao','stock' ,'unidade_medida', 'preco_a_granel','unidade_Medida_Por_Unidade', 'quantidade_por_unidade', 'preco_por_unidade','data_producao','marca' ]
        


