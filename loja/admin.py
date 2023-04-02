from django.contrib import admin
from .models import Utilizador, Consumidor, Fornecedor
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