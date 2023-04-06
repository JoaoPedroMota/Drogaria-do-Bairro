from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.loja, name='loja-home'),
    path('profile/',views.profile,name='profile'),
    path('',include('social_django.urls')),
    path('carrinho/', views.carrinho, name='loja-carrinho'),
    path('checkout/', views.checkout, name='loja-checkout'),
    path('login/', views.loginUtilizador, name='loja-login'),
    path('register/', views.registerUtilizador, name='loja-register-Utilizador'),
    path('logout', views.logutUtilizador, name='loja-logout'),
    path('form-fornecedor/', views.formFornecedor, name='loja-form-forcedor')
]
