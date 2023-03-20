from django.contrib import admin
from .models import Utilizador, Consumidor, Fornecedor
#Register your models here.

admin.site.register(Utilizador)
admin.site.register(Consumidor)
admin.site.register(Fornecedor)