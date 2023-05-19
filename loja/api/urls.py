from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

urlpatterns = [
    path('', views.getRotas),
    # utilizadores
    path('utilizadores/', views.UtilizadoresList.as_view()),
    path('utilizadores/<str:username>/', views.UtilizadoresDetail.as_view()),
    
    
    
    # consumidores
    path('consumidores/', views.ConsumidoresList.as_view()),
    path('consumidores/carrinhos/', views.CarrinhoList.as_view()),
    
    
    path('<str:username>/consumidor/', views.ConsumidoresDetail.as_view()),
    path('<str:username>/consumidor/carrinho/', views.ProdutosCarrinhoList.as_view()),

    
    # fornecedores
    path('fornecedores/', views.FornecedoresList.as_view()),
    path('<str:username>/fornecedor/', views.FornecedoresDetail.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/', views.UnidadeProducaoList.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/', views.UnidadeProducaoDetail.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<str:idUnidadeProducao>/veiculos/', views.getVeiculos),
    path('<str:username>/fornecedor/unidadesProducao/<str:idUnidadeProducao>/veiculos/<str:idVeiculo>/', views.getVeiculo),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/produtos/', views.ProdutoUnidadeProducaoList.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/produtos/<int:idProdutoUnidadeProducao>/', views.ProdutoUnidadeProducaoDetail.as_view()),
    
    
    
    # loja
    path('categorias/', views.CategoriaList.as_view()),
    path('categorias/<str:slug>/', views.CategoriaDetail.as_view()),
    
    
    path('produtos/', views.ProdutoList.as_view()),
    path('produtos/<str:slug>/', views.ProdutoDetail.as_view()),
    path('produtos_loja/',views.ProdutoUnidadeProducaoAll.as_view()),
    path('produtos_loja/em_stock/', views.ProdutoUnidadeProducaoEmStock.as_view()),
    path('produtos_loja/<int:idProduto>/', views.SingleProductDetails.as_view()),
    
]   
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
