from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.getRotas),
    path('utilizadores/', views.UtilizadoresList.as_view()),
    path('utilizadores/<str:idUtilizador>/', views.UtilizadoresDetail.as_view()),
    path('consumidores/', views.getConsumidores),
    path('consumidores/<str:idConsumidor>/', views.getConsumidor),
    path('fornecedores/', views.getFornecedores),
    path('fornecedores/<str:idFornecedor>/', views.getFornecedor),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/', views.getUPs),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/', views.getUP),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/veiculos/', views.getVeiculos),
    path('fornecedores/<str:idFornecedor>/unidadesProducao/<str:idUnidadeProducao>/veiculos/<str:idVeiculo>/', views.getVeiculo),
]
urlpatterns = format_suffix_patterns(urlpatterns)