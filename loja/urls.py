from django.urls import path, include
from . import views
from .views import removerUnidadeProducao, removerVeiculo, criar_produto, ver_produtos

urlpatterns = [
    path('api/', include('loja.api.urls')),
    path('', views.loja, name='loja-home'),
    path('about/', views.about, name='about'),
    #path('checkout/', views.checkout, name='loja-checkout'),
    path('login/', views.loginUtilizador, name='loja-login'),
    path('logout/', views.logout, name='loja-logout'),
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
    path('perfil/<str:userName>/unidadeProducao/<str:id>/editarUnidadeProducao/', views.editarUnidadeProducao, name='loja-editarUnidadeProducao'),
    path('<str:userName>/unidadeProducao/<int:id>/remover', removerUnidadeProducao, name='loja-removerUnidadeProducao'),
    path('criar-produto/<str:userName>/', views.criar_produto, name='loja-criarProduto'),
    path('shop/', views.ver_produtos, name='loja-ver-produtos'),
    path('shop/<int:produto_id>/', views.sP, name='loja-single-product'),
    path('carrinho/', views.carrinho, name='loja-carrinho'),
    path('adicionar-ao-carrinho/<int:produto_id>/', views.adicionar_ao_carrinho, name='loja-adicionar-ao-carrinho'),
    path('remover-do-carrinho/<int:produto_id>/', views.remover_do_carrinho, name='loja-remover-do-carrinho'),
    path('remover-produto-unidadeProducao/<int:idUnidadeProducao>/<int:idProdutoUnidadeProducao>/', views.removerAssociaoProdutoUP, name='loja-removerAssociaoProdutoUP'),
    path('associar-produto-unidade-producao/', views.criarAssociacaoProdutoUP, name="loja-associarProdutoUP"),
    path('detalhes-envio/', views.detalhesEnvio, name='loja-detalhesEnvio'),
    path('create_order/', views.create_order, name='create_order'),
    path('checkout/', views.checkout, name='loja-checkout'),
    path('perfil/<str:username>/encomenda/<int:idEncomenda>/produtos-encomendados/', views.getProdutosEncomenda,name='loja-produtosEncomendados'),
    
    path('confirmarDetalhesEnvio/', views.confirmarDetalhesEnvio, name='loja-confirmarDetalhesEnvio'),
    path('criarEncomenda/<int:idDetalhesEnvio>/', views.criarEncomenda, name='loja-criarEncomenda'),



]



