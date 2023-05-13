from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

urlpatterns = [
    path('', views.getRotas),
    path('utilizadores/', views.UtilizadoresList.as_view()),
    path('utilizadores/<str:idUtilizador>/', views.UtilizadoresDetail.as_view()),
    path('consumidores/', views.ConsumidoresList.as_view()),
    path('consumidores/<str:idConsumidor>/', views.ConsumidoresDetail.as_view()),
    path('fornecedores/', views.FornecedoresList.as_view()),
    path('fornecedores/<str:idFornecedor>/', views.FornecedoresDetail.as_view()),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/', views.UnidadeProducaoList.as_view()),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/', views.getUP),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/veiculos/', views.getVeiculos),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/veiculos/<str:idVeiculo>/', views.getVeiculo),
    path('categorias/', views.CategoriaList.as_view()),
    path('categorias/<str:nome>/', views.CategoriaDetail.as_view()),
    path('produtos/', views.ProdutoList.as_view()),
    path('produtos/<str:nome>/', views.ProdutoDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])