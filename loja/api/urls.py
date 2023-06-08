from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

urlpatterns = [
    path('', views.getRotas),
    # utilizadores
    path('utilizadores/', views.UtilizadoresList.as_view()),
    path('<str:username>/utilizadores/', views.UtilizadoresDetail.as_view()),
    
    
    
    # consumidores
    path('consumidores/', views.ConsumidoresList.as_view()),
    path('consumidores/carrinhos/', views.CarrinhoList.as_view()),
    
    path('consumidores/carrinhos/<int:idCarrinho>/', views.CarrinhoDetail.as_view()),
    

    path('<str:username>/consumidor/', views.ConsumidoresDetail.as_view()),
    path('<str:username>/consumidor/carrinho/', views.ProdutosCarrinhoList.as_view()),
    path('<str:username>/consumidor/carrinho/<int:idProdutoCart>/', views.ProdutosCarrinhoDetail.as_view()),
    path('<str:username>/consumidor/carrinho/produtoUP/<int:idProdutoUnidadeProducao>/', views.ProdutosCarrinhoDetailProdutoUP.as_view()),
    path('<str:username>/consumidor/detalhes_envio/', views.DetalhesEnvioList.as_view()),
    path('<str:username>/consumidor/detalhes_envio/<int:id>/', views.DetalhesEnvioDetails.as_view()),    

    path('<str:username>/consumidor/encomenda/', views.EncomendaList.as_view()),
    path('<str:username>/consumidor/encomenda/<int:idEncomenda>/', views.EncomendaDetail.as_view()),
    path('<str:username>/consumidor/encomenda/<int:idEncomenda>/produtos/', views.ProdutosEncomendaList.as_view()),
    path('<str:username>/consumidor/encomenda/<int:idEncomenda>/produtos/<int:idProdutoEncomenda>/', views.ProdutosEncomendaDetail.as_view()),
    path('<str:username>/consumidor/encomendarCarrinho/', views.EncomendarTodosOsProdutosCarrinho.as_view()),    
    path('<str:username>/consumidor/encomenda/<int:idEncomenda>/produtos/<int:idProdutoEncomenda>/cancelar/', views.ProdutoEncomendasCancelarView.as_view()),



    

    
    # fornecedores
    path('fornecedores/', views.FornecedoresList.as_view()),
    path('<str:username>/fornecedor/', views.FornecedoresDetail.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/', views.UnidadeProducaoList.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/', views.UnidadeProducaoDetail.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<str:idUnidadeProducao>/veiculos/', views.VeiculoList.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<str:idUnidadeProducao>/veiculos/<str:idVeiculo>/', views.VeiculoDetail.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/produtos/', views.ProdutoUnidadeProducaoList.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/produtos/<int:idProdutoUnidadeProducao>/', views.ProdutoUnidadeProducaoDetail.as_view()),
    path('unidadesProducao/<str:id>/', views.UnidadeProducaoDetailSoInfo.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/encomendas/',views.EncomendasPorUPList.as_view()),
    path('<str:username>/fornecedor/encomenda/<int:idEncomenda>/detalhes_envio/', views.getDetalhesParaForncedorDetails.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/veiculos/<int:idVeiculo>/carregar/', views.ProdutosEncomendadosVeiculosList.as_view()),
    path('<str:username>/fornecedor/unidadesProducao/<int:idUnidadeProducao>/veiculos/<int:idVeiculo>/sair/', views.VeiculoSaida.as_view()),
    
    #VeiculoSaida
    
    
    # loja
    path('categorias/', views.CategoriaList.as_view()),
    path('categorias/<int:id>/', views.CategoriaDetail.as_view()), #preciso ver isto
    path('categoriaNome/<str:nome>/', views.CategoriaDetailNome.as_view()),
    
    
    
    
    path('produtos/', views.ProdutoList.as_view()),
    path('produtos/<str:nome>/', views.ProdutoDetail.as_view()), #preciso ver isto
    path('produtosID/<str:id>/', views.ProdutoDetailID.as_view()),
    path('produtos_loja/',views.ProdutoUnidadeProducaoAll.as_view()),
    path('produtos_loja/em_stock/', views.ProdutoUnidadeProducaoEmStock.as_view()),
    path('produtos_loja/<int:idProduto>/', views.SingleProductDetails.as_view()),
    

]   


urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
