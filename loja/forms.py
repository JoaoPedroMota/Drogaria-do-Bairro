from django.forms import ModelForm, ModelChoiceField
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumbers import is_valid_number, parse as parseTelemovel
from django.db.models import Q
class UtilizadorFormulario(UserCreationForm):
    class Meta:
        model = Utilizador
        fields = ['first_name','last_name', 'username', 'email', 'password1', 'password2', 'pais','cidade','freguesia','morada','telemovel','tipo_utilizador','imagem_perfil']
  
class FornecedorFormulario(ModelForm):
    pass
    # class Meta:
    #     model = Fornecedor
    #     fields = ['descricao']
         
class EditarPerfil(ModelForm):
    class Meta:
        model = Utilizador
        fields = ['first_name', 'last_name', 'username','email', 'pais','cidade','freguesia','morada','telemovel','imagem_perfil',]

class CompletarPerfil(ModelForm):
    telemovel = PhoneNumberField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = Utilizador
        fields = ['first_name', 'last_name', 'username','email', 'pais','cidade','freguesia','morada','telemovel','tipo_utilizador', 'imagem_perfil']

class criarUnidadeProducaoFormulario(ModelForm):
    class Meta:
        model= UnidadeProducao
        fields = ['nome', 'pais','cidade','freguesia','morada', 'tipo_unidade']
        widgets = {
            'tipo_unidade': forms.Select(choices=UnidadeProducao.TIPO_UNIDADE)
        }

class criarVeiculoFormulario(ModelForm):
    class Meta:
        model=Veiculo
        fields = ['nome', 'tipo_veiculo']

class editarVeiculoFormulario(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_veiculo'].choices = [
            ('D', 'Disponível'),
            ('I/M', 'Indisponível/Manutenção')
        ]
    class Meta:
        model=Veiculo
        fields = ['nome', 'estado_veiculo']

class editarUnidadeProducaoFormulario(ModelForm):
    class Meta:
        model=UnidadeProducao
        fields = ['nome', 'pais','cidade','morada','freguesia' ,'tipo_unidade']

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

class editarProdutoUnidadeProducaoForm(forms.ModelForm):
    data_producao = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    imagem_produto = forms.ImageField(required=False)
    class Meta:
        model = ProdutoUnidadeProducao
        fields = ["descricao","stock" ,"unidade_medida", "preco_a_granel","unidade_Medida_Por_Unidade", "quantidade_por_unidade", "preco_por_unidade","data_producao","marca", "imagem_produto"]
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(editarProdutoUnidadeProducaoForm, self).__init__(*args, **kwargs)

    
class DetalhesEnvioForm(forms.ModelForm):
    class Meta:
        model = DetalhesEnvio
        fields = ['nome', 'pais', 'cidade', 'morada', 'telemovel', 'email', 'instrucoes_entrega', 'usar_informacoes_utilizador', 'guardar_esta_morada']
    
    def __init__(self, *args, **kwargs):
        utilizador = kwargs.pop('utilizador', None)
        consumidor = utilizador.consumidor
        super().__init__(*args, **kwargs)
        self.fields['usar_informacoes_utilizador'].required = False
        self.fields['usar_informacoes_utilizador'].initial = True
        self.fields['guardar_esta_morada'].initial = True
        if consumidor:
            self.initial['consumidor'] = consumidor
        if self.fields['usar_informacoes_utilizador'].initial == True:
            self.fields['usar_informacoes_utilizador'].widget.attrs['checked'] = 'checked'
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
        utilizador = consumidor.utilizador
        telemovel = cleaned_data.get('telemovel') if cleaned_data.get('telemovel') is not None else None
        if usar_informacoes_utilizador:
            if cleaned_data['nome'] != utilizador.nome:
                self.add_error("nome", f"Selecionou utilizar informações do utilizador, logo o nome tem de ser igual ao que está definido na conta: {utilizador.nome}")
            if cleaned_data['pais'] != utilizador.pais:
                self.add_error("pais", f"Selecionou utilizar informações do utilizador, logo o pais tem de ser igual ao que está definido na conta: {utilizador.pais.name}")
            if cleaned_data['cidade'] != utilizador.cidade:
                self.add_error('cidade',f"Selecionou utilizar informações do utilizador, logo a cidade tem de ser igual à que está definido na conta: {utilizador.cidade} (tudo maiúsculas)")
            if telemovel != None:
                if cleaned_data['telemovel'] != utilizador.telemovel:
                    self.add_error('telemovel',f"Selecionou utilizar informações do utilizador, logo o telemóvel tem de ser igual ao que está definido na conta: {utilizador.telemovel}")
            if telemovel is None:
                self.add_error('telemovel',f"Introduza um número de telemóvel válido. No caso do telemóvel não for de Portugal, tem de inserir o prefixo internacional.")
            if (utilizador.morada is None or utilizador.morada == ''): #utilizador ainda não tem morada
                    moradinha= cleaned_data.get('morada') if cleaned_data.get('morada') is not None else ''
                    vazio = moradinha.replace(" ","")
                    # print(vazio=='')
                    if vazio == '':

                        self.add_error('morada',f"Selecionou utilizar informações do utilizador, mas o utilizador ainda não tem nenhuma morada guardada. Por favor adicone uma morada válida.")
            if utilizador.morada is not None and utilizador.morada != cleaned_data.get('morada'):
                self.add_error('morada',f"Selecionou utilizar informações do utilizador, logo a morada tem de ser igual à que está definida no utilizador: {utilizador.morada}. (Se pretender alterar apenas a morada, vá a Editar Perfil)")
            if cleaned_data['email'] != utilizador.email:
                self.add_error('email',f"Selecionou utilizar informações do utilizador, logo o email tem de ser igual ao que está definida no utilizador: {utilizador.email}")
        return cleaned_data



class DateRangeForm(forms.Form):
    dataInicio = forms.DateField(
        label='Data de Início',
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
        required=False  # torna o campo não obrigatório
    )
    dataFim = forms.DateField(
        label='Data de Fim',
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
        required=False  # torna o campo não obrigatório
    )
    def clean(self):
        cleaned_data = super().clean()
        dataInicio = cleaned_data.get('dataInicio')
        dataFim = cleaned_data.get('dataFim')

        if dataInicio and dataFim and dataInicio >= dataFim:
           self.add_error('dataInicio', "A data início tem de ser anterior à data de fim")
           self.add_error('dataFim', "A data fim tem de ser posterior à data de início")
        else:
            return cleaned_data

class ConfirmarDetalhesEnvioForm(forms.ModelForm):
    class Meta:
        model = DetalhesEnvio
        fields = ['nome', 'pais', 'cidade', 'morada', 'telemovel', 'email', 'instrucoes_entrega','guardar_esta_morada']
    
    def __init__(self, *args, **kwargs):
        utilizador = kwargs.pop('utilizador', None)
        consumidor = utilizador.consumidor
        validarNovosDetalhes=kwargs.pop('validarNovosDetalhes', None)
        # print("VALIDAR NOVOS DETALHES (init): ", validarNovosDetalhes)

        super().__init__(*args, **kwargs)
        if consumidor:
            self.initial['consumidor'] = consumidor
            self.initial['validarNovosDetalhes']= validarNovosDetalhes
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
        morada = cleaned_data['morada'] if cleaned_data.get('morada') is not None else None
        consumidor = self.initial.get('consumidor')
        validarNovosDetalhes= self.initial.get('validarNovosDetalhes')
        utilizador = consumidor.utilizador
        telemovel = cleaned_data.get('telemovel') if cleaned_data.get('telemovel') is not None else None
        # print("VALIDAR NOVOS DETALHES (clean): ", validarNovosDetalhes)

        if cleaned_data['nome'] is None or cleaned_data['nome'] == "":
            self.add_error("nome", f"Selecione um nome")
        if cleaned_data['pais'] is None or cleaned_data['pais'] == "":
            self.add_error("pais", f"Selecinoe um país")
        if cleaned_data['cidade'] is None or cleaned_data['cidade'] == "":
            self.add_error('cidade',f"Selecione uma cidade")
        if telemovel is None or telemovel == "":
            self.add_error('telemovel',f"Introduza um número de telemóvel válido. No caso do telemóvel não for de Portugal, tem de inserir o prefixo internacional.")
        if morada is None:
            self.add_error('morada',f"Selecione uma morada")
        if morada is not None:
            moradinha= cleaned_data.get('morada')
            vazio = moradinha.replace(" ","")
            if vazio == '':
                self.add_error('morada',f"Selecionou utilizar informações do utilizador, mas o utilizador ainda não tem nenhuma morada guardada. Por favor adicone uma morada válida.")
        if validarNovosDetalhes==False and cleaned_data['guardar_esta_morada']==False:
            self.add_error("guardar_esta_morada", "Erro - Ainda não tem detalhes de envio associados ao seu perfil. Na primeira encomenda é obrigatório guardar os detalhes")

        if cleaned_data['email'] is None or cleaned_data['email'] == "":
            self.add_error('email',f"Selecione um email")
        return cleaned_data



class CancelarProdutoEncomendadoForm():
    nome_produto = forms.CharField()
    
    
    
class ProdutosEncomendadosVeiculosForm(forms.ModelForm):
    veiculo = forms.ModelChoiceField(queryset=Veiculo.objects.filter())
    def __init__(self, *args, **kwargs):
        idUnidadeProducao = kwargs.pop('idUnidadeProducao',)
        super().__init__(*args, **kwargs)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(
            Q(unidadeProducao_id=idUnidadeProducao) &
            (
                Q(estado_veiculo='D') | Q(estado_veiculo="C")
            )
            )

    class Meta:
        model = ProdutosEncomendadosVeiculos
        fields = ['veiculo']



#########################################
class AtributoForm(forms.ModelForm):
    class Meta:
        model = Atributo
        fields = ['nome']
# class OpcaoForm(forms.ModelForm):
#     class Meta:
#         model = Opcao
#         fields = ['nome', 'atributos']
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'categoria_pai']

class ProdutoOpcaoForm(forms.ModelForm):
    class Meta:
        model = ProdutoOpcao
        fields = ['produto', 'opcao']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'opcao': forms.Select(attrs={'class': 'form-control'}),
        }
from django import forms

class OpcaoForm(forms.Form):
    opcoes = forms.MultipleChoiceField(
        label='Opções',
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, opcoes_por_atributo=None, *args, **kwargs):
        super(OpcaoForm, self).__init__(*args, **kwargs)
        print("OPCOES POR ATRIBUTO")
        print(opcoes_por_atributo)
        if opcoes_por_atributo:
            choices = []
            for atributo, opcoes in opcoes_por_atributo.items():
                choices.extend([(opcao, opcao) for opcao in opcoes])

            # print("1 opcoes!!!!!",opcoes)
            # print("2 opcoes_por_atributo!!!!!",opcoes_por_atributo)
            self.fields['opcoes'].choices = choices
            # print("3 opcoes!!!!!!!!",opcoes)
            # print("4 opcoes_por_atributo!!!",opcoes_por_atributo)


