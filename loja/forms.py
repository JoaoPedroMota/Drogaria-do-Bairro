from django.forms import ModelForm
from .models import Utilizador, Fornecedor
from django.contrib.auth.forms import UserCreationForm

class UtilizadorFormulario(UserCreationForm):
    class Meta:
        model = Utilizador
        fields = ['nome', 'username', 'email', 'password1', 'password2', 'pais','cidade','morada','telemovel','tipo_utilizador','imagem_perfil']
        
        
        
class FornecedorFormulario(ModelForm):
    class Meta:
        model = Fornecedor
        fields = '__all__'
        exclude = {'utilizador'}
        
        
        
class EditarPerfil(ModelForm):
    class Meta:
        model = Utilizador
        fields = ['nome', 'username','email', 'pais','cidade','telemovel','imagem_perfil',]