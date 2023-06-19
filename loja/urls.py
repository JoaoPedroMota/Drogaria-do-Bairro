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
    path('perfil/<str:username>/editarPerfil/', views.editarPerfil, name='loja-editarPerfil'),
    path('completarPerfil/', views.completarPerfil, name='loja-completarPerfil'),
    path('apagar-conta/<str:pk>/', views.apagarConta, name='loja-delete-conta'),
    path('perfil/<str:userName>/', views.perfil, name='loja-perfil'),
    path('perfil/<str:userName>/criarUP/', views.criarUP, name='loja-criarUP'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/', views.unidadeProducao, name='loja-unidadeProducao'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/criarVeiculo/', views.criarVeiculo, name="loja-criarVeiculo"),
    path('removerVeiculo/<str:userName>/<int:id>/', removerVeiculo, name='loja-removerVeiculo'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/editarVeiculo/<str:idVeiculo>/', views.editarVeiculo, name='loja-editarVeiculo'),
    path('perfil/<str:userName>/unidadeProducao/<str:id>/editarUnidadeProducao/', views.editarUnidadeProducao, name='loja-editarUnidadeProducao'),
    path('<str:userName>/unidadeProducao/<int:id>/remover/', removerUnidadeProducao, name='loja-removerUnidadeProducao'),
    path('criar-produto/<str:userName>/', views.criar_produto, name='loja-criarProduto'),
    path('shop/', views.ver_produtos, name='loja-ver-produtos'),
    path('shop/<int:produto_id>/', views.sP, name='loja-single-product'),
    path('carrinho/', views.carrinho, name='loja-carrinho'),
    path('adicionar-ao-carrinho/<int:produto_id>/', views.adicionar_ao_carrinho, name='loja-adicionar-ao-carrinho'),
    path('remover-do-carrinho/<int:produto_id>/', views.remover_do_carrinho, name='loja-remover-do-carrinho'),
    path('<str:username>/remover-produto-unidadeProducao/<int:idUnidadeProducao>/<int:idProdutoUnidadeProducao>/', views.removerAssociaoProdutoUP, name='loja-removerAssociaoProdutoUP'),
    path('perfil/<str:username>/associar-produto-unidade-producao/', views.criarAssociacaoProdutoUP, name="loja-associarProdutoUP"),
    path('editar_produto_unidadeProducao/<int:idUnidadeProducao>/<int:idProdutoUnidadeProducao>/', views.editarAssociacaoProdutoUP, name='loja-editarAssociacaoProdutoUP'),
    path('perfil/<str:username>/detalhes-envio/', views.detalhesEnvio, name='loja-detalhesEnvio'),
    path('checkout/', views.checkout, name='loja-checkout'),
    path('perfil/<str:username>/encomenda/<int:idEncomenda>/produtos-encomendados/', views.getProdutosEncomenda,name='loja-produtosEncomendados'),
    path('perfil/<str:username>/detalhesPorEncomenda/<int:idEncomenda>/<str:idDetalhes>/', views.verDetalhesEnvioNaEncomenda, name='loja-detalhes-por-encomenda'),
    path('confirmarDetalhesEnvio/', views.confirmarDetalhesEnvio, name='loja-confirmarDetalhesEnvio'),
    path('criarEncomenda/<int:idDetalhesEnvio>/', views.criarEncomenda, name='loja-criarEncomenda'),
    path('perfil/<str:username>/encomenda/<int:idEncomenda>/produtos-encomendados/<int:idProdutoEncomendado>/cancelar/<str:nomeProduto>/', views.cancelarProdutoEncomendado, name="loja-cancelarProdutosEncomendados"),
    path('perfil/<str:username>/unidadeProducao/<int:idUnidadeProducao>/encomenda/<int:idEncomenda>/detalhes-envio/<int:idProdutoEncomendado>/', views.getDetalhesParaFornecedor, name='loja-detalhes-envio-fornecedor'),
    path('perfil/<str:username>/unidadeProducao/<int:idUnidadeProducao>/colocarEncomendaEmVeiculo/<int:idProdutoEncomenda>/', views.colocarProdutoEmVeiculoTransporte, name="loja-colocar-encomenda-veiculo"),
    path('perfil/<str:username>/unidadesProducao/<int:idUnidadeProducao>/veiculos/<int:idVeiculo>/sairParaEntrega/', views.veiculoSairParaEntrega, name='loja-veiculoSairEntrega'),
    path('perfil/<str:username>/unidadesProducao/<int:idUnidadeProducao>/veiculos/<int:idVeiculo>/entregarEncomenda/', views.entregarEncomenda, name='loja-entregarEncomenda'),
    path('perfil/<str:username>/unidadesProducao/<int:idUnidadeProducao>/veiculos/<int:idVeiculo>/veiculoRegressou/', views.veiculoRegressou, name='loja-veiculoRegressou'),
    path('notificacoes/<str:username>/', views.obterNotificacoesF, name='notificacoes'),
    path('delete-notifications/<str:username>', views.marcar_notificacao_lida, name='marcar-lido'),
    
]



