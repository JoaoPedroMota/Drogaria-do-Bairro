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
<<<<<<< HEAD
    class Meta:
        model = Fornecedor
        fields = ['descricao']
                
=======
    pass
        
        
        
>>>>>>> e4331d2f1820222e390adceb697c187bd4f3d528
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

<<<<<<< HEAD
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
        fields = ['descricao', 'categoria', 'preco', 'unidade_medida', 'preco_por_unidade','data_producao', 'marca']
        
=======
# class ProdutoForm(forms.ModelForm):
#     data_validade = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     data_producao = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     categoria = forms.CharField(max_length=100, required=True)
#     marca = forms.CharField(max_length=50)
#     class Meta:
#         model = Produto
#         fields = ['nome', 'descricao', 'categoria', 'preco', 'unidade_medida', 'data_validade', 'data_producao', 'unidade_producao', 'marca']
>>>>>>> e4331d2f1820222e390adceb697c187bd4f3d528

