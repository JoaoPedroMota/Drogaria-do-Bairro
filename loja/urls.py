from django.urls import path
from . import views

urlpatterns = [
    path('', views.loja, name='loja-home'),
    path('carrinho/', views.carrinho, name='loja-carrinho'),
    path('checkout/', views.checkout, name='loja-checkout'),
    path('login/', views.loginUtilizador, name='loja-login'),
    path('register/', views.registerUtilizador, name='loja-register-Utilizador'),
    path('logout', views.logutUtilizador, name='loja-logout'),
    path('form-fornecedor/', views.formFornecedor, name='loja-form-forcedor'),
    path('editarPerfil/', views.editarPerfil, name='loja-editarPerfil'),
    path('apagar-conta/<str:pk>/', views.apagarConta, name='loja-delete-conta'),
    path('perfil/<str:userName>/', views.perfil, name='loja-perfil'),
    path('perfil/<str:userName>/criarUP/', views.criarUP, name='loja-criarUP'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/', views.unidadeProducao, name='loja-unidadeProducao'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/criarVeiculo/', views.criarVeiculo, name="loja-criarVeiculo"),
]



