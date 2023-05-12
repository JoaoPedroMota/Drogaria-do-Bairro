from django.contrib import admin
<<<<<<< HEAD
#from .models import Utilizador, Consumidor, Fornecedor, Veiculo, UnidadeProducao
from .models import Utilizador, Consumidor, Fornecedor, Veiculo, UnidadeProducao, Produto, Categoria, CategoriaAtributo, Atributo, ProdutoUnidadeProducao
from .imagem import Imagem


#Register your models here.

class MyModel(admin.ModelAdmin):
    """Para ver o id na base de dados.
    Retirar quando não for necessário.

    Args:
        admin (_type_): _description_
    """
    readonly_fields=('id',)


admin.site.register(Utilizador, MyModel)
admin.site.register(Consumidor, MyModel)
admin.site.register(Fornecedor, MyModel)
admin.site.register(Veiculo, MyModel)
admin.site.register(UnidadeProducao, MyModel)



# admin.site.register(Produto, MyModel)
# admin.site.register(Categoria, MyModel)
# admin.site.register(CategoriaAtributo, MyModel)
# admin.site.register(Atributo, MyModel)
# admin.site.register(Imagem, MyModel)
# admin.site.register(ProdutoUnidadeProducao, MyModel)

admin.site.register(Carrinho, MyModel)
admin.site.register(ProdutosCarrinho, MyModel)

