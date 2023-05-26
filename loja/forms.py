from django.forms import ModelForm, ModelChoiceField
from django import forms
from .models import Utilizador, Fornecedor, UnidadeProducao,Categoria , Veiculo, Produto, ProdutoUnidadeProducao
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django_countries.widgets import CountrySelectWidget
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

class CompletarPerfil(ModelForm):
    class Meta:
        model = Utilizador
        fields = ['first_name', 'last_name', 'username','email', 'pais','cidade','telemovel','tipo_utilizador', 'imagem_perfil']

class criarUnidadeProducaoFormulario(ModelForm):
    class Meta:
        model= UnidadeProducao
        fields = ['nome', 'pais','cidade','morada', 'tipo_unidade']
        widgets = {
            'tipo_unidade': forms.Select(choices=UnidadeProducao.TIPO_UNIDADE)
        }

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

class PasswordConfirmForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)




class ProdutoAPIForm(forms.ModelForm):
    categoria = ModelChoiceField(queryset=Categoria.objects.exclude(id__in=Categoria.objects.values_list('categoria_pai', flat=True).filter(categoria_pai__isnull=False)))
    class Meta:
        model = Produto
        fields = ['nome', 'categoria']

class ProdutoForm(forms.ModelForm):
    categoria = ModelChoiceField(queryset=Categoria.objects.exclude(id__in=Categoria.objects.values_list('categoria_pai', flat=True).filter(categoria_pai__isnull=False)))
    class Meta:
        model = Produto
        fields = ['nome', 'categoria']
    def clean_nome(self):
        nome_produto = self.cleaned_data['nome']
        if Produto.objects.filter(nome=nome_produto).exists():
            raise forms.ValidationError(
                'Já existe um produto com este nome. Caso deseje criar mesmo um novo produto, altere o nome do produto a ser criado',
                code='product_name_exists'
            )
        return nome_produto

class ProdutoUnidadeProducaoForm(forms.ModelForm):
    data_producao = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    produto = forms.ModelChoiceField(queryset=Produto.objects.all())
    unidade_producao = forms.ModelChoiceField(queryset=UnidadeProducao.objects.filter())
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ['produto', 'unidade_producao', 'descricao','stock' ,'unidade_medida', 'preco_a_granel','unidade_Medida_Por_Unidade', 'quantidade_por_unidade', 'preco_por_unidade','data_producao','marca' ]
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProdutoUnidadeProducaoForm, self).__init__(*args, **kwargs)
        self.fields['unidade_producao'].queryset = UnidadeProducao.objects.filter(fornecedor__utilizador=self.user)
    