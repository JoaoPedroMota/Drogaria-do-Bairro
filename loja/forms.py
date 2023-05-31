from django.forms import ModelForm, ModelChoiceField
from django import forms
from .models import Utilizador, Fornecedor, UnidadeProducao,Categoria , Veiculo, Produto, ProdutoUnidadeProducao, DetalhesEnvio
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumbers import is_valid_number, parse as parseTelemovel
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
    telemovel = PhoneNumberField(required=True)
    
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
    data_producao = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    produto = forms.ModelChoiceField(queryset=Produto.objects.all())
    unidade_producao = forms.ModelChoiceField(queryset=UnidadeProducao.objects.filter())
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ["produto", "unidade_producao", "descricao","stock" ,"unidade_medida", "preco_a_granel","unidade_Medida_Por_Unidade", "quantidade_por_unidade", "preco_por_unidade","data_producao","marca", "imagem_produto"]
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ProdutoUnidadeProducaoForm, self).__init__(*args, **kwargs)
        self.fields["unidade_producao"].queryset = UnidadeProducao.objects.filter(fornecedor__utilizador=self.user)
    def verificar_existencia_associacao(self, produto, unidade_producao):
        existe_associacao = False

        if produto and unidade_producao:
            # Faça a verificação aqui e atribua o resultado à variável existe_associacao
            existe_associacao = ProdutoUnidadeProducao.objects.filter(produto=produto, unidade_producao=unidade_producao).exists()

        return existe_associacao
    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get("produto")
        unidade_producao = cleaned_data.get("unidade_producao")
        unidade_medida = cleaned_data.get("unidade_medida")
        preco_a_granel = cleaned_data.get("preco_a_granel")
        unidade_Medida_Por_Unidade = cleaned_data.get("unidade_Medida_Por_Unidade")
        quantidade_por_unidade = cleaned_data.get("quantidade_por_unidade")
        preco_por_unidade = cleaned_data.get("preco_por_unidade")

        if self.verificar_existencia_associacao(produto, unidade_producao):
            self.add_error('produto', f'Já existe este produto ({produto}) nesta unidade de produção ({unidade_producao}). Não pode ter o mesmo produto na mesma unidade de produção. Altere um dos campos.')
            self.add_error('unidade_producao',f'Já existe este produto ({produto}) nesta unidade de produção ({unidade_producao}). Não pode ter o mesmo produto na mesma unidade de produção. Altere um dos campos.')
        
        if unidade_medida == "un":
            if preco_a_granel is not None:
                self.add_error("preco_a_granel", "O preço a granel não é permitido para produtos vendidos à unidade. Remova a este campo.")
            if unidade_Medida_Por_Unidade is None:
                self.add_error("unidade_Medida_Por_Unidade", "Tem de introduzir a unidade de media da embalagem/unidade. Preencha o campo  'unidade_Medida_Por_Unidade' ")
            if quantidade_por_unidade is None:
                self.add_error("quantidade_por_unidade", "A quantidade por unidade é obrigatória para produtos vendidos à unidade. Preencha o campo 'quantidade_por_unidade' ")
            if preco_por_unidade is None:
                self.add_error("preco_por_unidade", "O preço por unidade é obrigatório para produtos vendidos à unidade.")

        elif unidade_medida in ("kg", "g", "l", "ml"):
            if unidade_Medida_Por_Unidade is not None:
                self.add_error("unidade_Medida_Por_Unidade", f"Selecionou antes {dict(ProdutoUnidadeProducao.UNIDADES_MEDIDA_CHOICES).get(unidade_medida)} como unidade de medida deste produto. Este campo serve para indicar qual a unidade de medida do produto à venda. Remova a seleção do campo unidade de medida por unidade.")
            if quantidade_por_unidade is not None:
                self.add_error("quantidade_por_unidade", "A quantidade por unidade não é permitida para produtos vendidos por peso ou volume. Remova este campo.")
            if preco_por_unidade is not None:
                self.add_error("preco_por_unidade", "O preço por unidade não é permitido para produtos vendidos por peso ou volume. Remova este campo.")
            if preco_a_granel is None:
                self.add_error("preco_a_granel", "O preço a granel é obrigatório para produtos vendidos por peso ou volume. Preencha o campo: Preço a granel.")

        else:
            if unidade_medida == "un":
                if unidade_Medida_Por_Unidade is None:
                    self.add_error("unidade_Medida_Por_Unidade", "A unidade de medida para produtos vendidos à unidade é obrigatória. Preencha o campo: Unidade Medida Por Unidade")
                if quantidade_por_unidade is None:
                    self.add_error("quantidade_por_unidade", "A quantidade para produtos vendidos à unidade é obrigatória. Preencha o campo: Quantidade por unidade")
                if preco_por_unidade is None:
                    self.add_error("preco_por_unidade", "O preço por produtos vendidos à unidade é obrigatório. Preencha o campo: Preço por unidade")
            elif unidade_medida in ["kg", "g", "l", "ml"]:
                if preco_a_granel is None:
                    self.add_error("preco_a_granel", 'O preço a granel é obrigatório para produtos vendidos por peso ou volume. Preencha o campo: Preço a granel.')



class DetalhesEnvioForm(forms.ModelForm):
    class Meta:
        model = DetalhesEnvio
        fields = ['nome_morada', 'nome', 'pais', 'cidade', 'morada', 'telemovel', 'email', 'instrucoes_entrega', 'usar_informacoes_utilizador']
    
    def __init__(self, *args, **kwargs):
        utilizador = kwargs.pop('utilizador', None)
        consumidor = utilizador.consumidor
        super().__init__(*args, **kwargs)
        self.fields['usar_informacoes_utilizador'].required = False
        self.fields['usar_informacoes_utilizador'].initial = True
        if consumidor:
            self.initial['consumidor'] = consumidor
        if self.fields['usar_informacoes_utilizador']:
            utilizador = self.initial['consumidor'].utilizador
            self.fields['nome'].initial = utilizador.nome
            self.fields['pais'].initial = utilizador.pais
            self.fields['cidade'].initial = utilizador.cidade
            if utilizador.morada is not None:
                self.fields['morada'].initial = utilizador.morada
            self.fields['telemovel'].initial = utilizador.telemovel
            self.fields['email'].initial = utilizador.email
    
    def clean(self):
        cleaned_data = super().clean()
        usar_informacoes_utilizador = cleaned_data.get('usar_informacoes_utilizador')
        consumidor = self.initial.get('consumidor')

        if usar_informacoes_utilizador and consumidor:
            utilizador = consumidor.utilizador
            cleaned_data['nome'] = utilizador.nome
            cleaned_data['pais'] = utilizador.pais
            cleaned_data['cidade'] = utilizador.cidade
            cleaned_data['telemovel'] = utilizador.telemovel
            cleaned_data['email'] = utilizador.email

        return cleaned_data
