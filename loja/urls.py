from django.urls import path, include
from . import views
from .views import removerUnidadeProducao, removerVeiculo, criar_produto, ver_produtos

urlpatterns = [
    path('api/', include('loja.api.urls')),
    path('', views.loja, name='loja-home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('news/', views.news, name='news'),
    path('carrinho/', views.carrinho, name='loja-carrinho'),
    path('checkout/', views.checkout, name='loja-checkout'),
    path('login/', views.loginUtilizador, name='loja-login'),
    path('logout', views.logout, name='loja-logout'),
    path('callback', views.callback, name='loja-callback'),
    # path('register/', views.registerUtilizador, name='loja-register-Utilizador'),
    # path('form-fornecedor/', views.formFornecedor, name='loja-form-forcedor'),
    path('editarPerfil/', views.editarPerfil, name='loja-editarPerfil'),
    path('completarPerfil/', views.completarPerfil, name='loja-completarPerfil'),
    path('apagar-conta/<str:pk>/', views.apagarConta, name='loja-delete-conta'),
    path('perfil/<str:userName>/', views.perfil, name='loja-perfil'),
    path('perfil/<str:userName>/criarUP/', views.criarUP, name='loja-criarUP'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/', views.unidadeProducao, name='loja-unidadeProducao'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/criarVeiculo/', views.criarVeiculo, name="loja-criarVeiculo"),
    path('removerVeiculo/<str:userName>/<int:id>/', removerVeiculo, name='loja-removerVeiculo'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/editarVeiculo/<str:idVeiculo>', views.editarVeiculo, name='loja-editarVeiculo'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/editarUnidadeProducao', views.editarUnidadeProducao, name='loja-editarUnidadeProducao'),
    path('<str:userName>/unidadeProducao/<int:id>/remover', removerUnidadeProducao, name='loja-removerUnidadeProducao'),
    path('criar_produto/<str:userName>/<int:id>', views.criar_produto, name='loja-criarProduto'),
    path('shop/', views.ver_produtos, name='ver_produtos'),
]



