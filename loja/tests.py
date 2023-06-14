import phonenumbers
from django.test import TestCase
from loja.models import *

class UtilizadorModelTesting(TestCase):

    def setUp(self):
        self.utilizadorConsumidor = Utilizador.objects.create(
            email='testconsumidor@teste.com',
            first_name='Consumidor',
            last_name='Caso de Teste',
            nome='Consumidor Caso de Teste',  # Adicionado manualmente
            username='testconsumidor',
            pais='PT',
            cidade='Lisboa',
            freguesia='Arroios',
            telemovel='+351912345678',
            tipo_utilizador=Utilizador.CONSUMIDOR
        )
        self.utilizadorFornecedor = Utilizador.objects.create(
            email='testfornecedor@teste.com',
            first_name='Fornecedor',
            last_name='Caso de Teste',
            nome='Fornecedor Caso de Teste',  # Adicionado manualmente
            username='testFornecedor',
            pais='PT',
            cidade='Lisboa',
            freguesia='Anjos',
            telemovel='+351912345679',
            tipo_utilizador=Utilizador.FORNECEDOR
        )
        self.consumidor = Consumidor.objects.create(utilizador=self.utilizadorConsumidor)
        self.carrinho = Carrinho.objects.create(consumidor=self.consumidor)
    
    def test_eh_instacia(self):
        utilizador = self.utilizadorConsumidor
        self.assertIsInstance(utilizador, Utilizador)
    def test_eh_consumidor(self):
        self.assertTrue(self.utilizadorConsumidor.is_consumidor)
    def test_associar_utilizador_carrinho(self):
        self.assertTrue(hasattr(self.utilizadorConsumidor, 'consumidor'))
    def test_cria_intacia_consumidor(self):
        self.assertIsInstance(self.utilizadorConsumidor.consumidor, Consumidor)
    def test_tem_carrinho(self):
        self.assertTrue(hasattr(self.utilizadorConsumidor.consumidor, 'carrinho'))
    def test_tem_carrinho(self):
        self.assertIsInstance(self.utilizadorConsumidor.consumidor.carrinho, Carrinho)
    def test_utilizador_has_perm(self):
        self.assertFalse(self.utilizadorConsumidor.has_perm("perm"))
    def test_utilizador_has_module_perms(self):
        self.assertFalse(self.utilizadorConsumidor.has_module_perms("app_label"))
    def test_utilizador_str(self):
        self.assertEqual(str(self.utilizadorConsumidor), 'testconsumidor')
    def test_utilizador_repr(self):
        representacao = f"Utilizador(nome='{self.utilizadorConsumidor.nome}', email='{self.utilizadorConsumidor.email}', username='{self.utilizadorConsumidor.username}', pais='{self.utilizadorConsumidor.pais}', cidade='{self.utilizadorConsumidor.cidade}', freguesia='{self.utilizadorConsumidor.freguesia}', telemovel='{self.utilizadorConsumidor.telemovel}', tipo_utilizador='{self.utilizadorConsumidor.tipo_utilizador}', imagem_perfil='{self.utilizadorConsumidor.imagem_perfil}', is_staff={self.utilizadorConsumidor.is_staff}, is_admin={self.utilizadorConsumidor.is_admin}, updated='{self.utilizadorConsumidor.updated}', created='{self.utilizadorConsumidor.created}')"
        self.assertEquals(repr(self.utilizadorConsumidor), representacao)
    def test_cria_utilizador_fornecedor_(self):
        self.assertIsInstance(self.utilizadorFornecedor, Utilizador)
    def test_utilizador_is_fornecedor(self):
        self.assertTrue(self.utilizadorFornecedor.is_fornecedor)




class ConsumidorTesting(TestCase):
    def setUp(self):
        self.utilizador = Utilizador.objects.create(
            email='testconsumidorclasse@teste.com',
            first_name='Consumidor',
            last_name='Caso de Teste',
            nome='Consumidor Caso de Teste',  # Adicionado manualmente
            username='testconsumidorclasse',
            pais='PT',
            cidade='Lisboa',
            freguesia="Areeiro",
            telemovel='+351912345679',
            tipo_utilizador=Utilizador.CONSUMIDOR
        )
        self.consumidor = Consumidor.objects.create(utilizador=self.utilizador)
    def test_cria_consumidor(self):
        self.assertTrue(isinstance(self.consumidor, Consumidor))
    def test_str_consumidor(self):
        self.assertEqual(str(self.consumidor), self.utilizador.username)
    def test_raise_error_ja_eh_fornecedor(self):
        utilizadorTEMP =         self.utilizador = Utilizador.objects.create(
            email='testconsumidorclassetemp@teste.com',
            first_name='Consumidor',
            last_name='Caso de Teste',
            nome='Consumidor Caso de Teste',  # Adicionado manualmente
            username='testconsumidorclassetemp',
            pais='PT',
            cidade='Lisboa',
            freguesia="Avenidas Novas",
            telemovel='+351912345680',
            tipo_utilizador=Utilizador.FORNECEDOR
        )
        fornecedor = Fornecedor.objects.create(utilizador=utilizadorTEMP)
        with self.assertRaises(ValueError):
            Consumidor.objects.create(utilizador=utilizadorTEMP)
            raise ValueError('O utilizador já está associado a um Fornecedor.')
    def test_raise_error_user_n_eh_consumidor(self):
        utilizadorTEMP =         self.utilizador = Utilizador.objects.create(
            email='testconsumidorclassetemp2@teste.com',
            first_name='Consumidor',
            last_name='Caso de Teste',
            nome='Consumidor Caso de Teste',  # Adicionado manualmente
            username='testconsumidorclassetemp2',
            pais='PT',
            cidade='Lisboa',
            freguesia="Lumiar",
            telemovel='+351912345681',
            tipo_utilizador=Utilizador.FORNECEDOR
        )
        with self.assertRaises(ValueError):
            Consumidor.objects.create(utilizador=utilizadorTEMP)
            raise ValueError('O utilizador não é um consumidor')
        
        



class FornecedorTesting(TestCase):
    def setUp(self):
        self.utilizador = Utilizador.objects.create(
            email='testFornecedorclasse@teste.com',
            first_name='Fornecedor',
            last_name='Caso de Teste',
            nome='Fornecedor Caso de Teste',  # Adicionado manualmente
            username='testFornecedorclasse',
            pais='PT',
            cidade='Lisboa',
            freguesia = "Belém",
            telemovel='+351912345682',
            tipo_utilizador=Utilizador.FORNECEDOR
        )
        self.fornecedor = Fornecedor.objects.create(utilizador=self.utilizador)
    def test_cria_consumidor(self):
        self.assertTrue(isinstance(self.fornecedor, Fornecedor))
    def test_str_consumidor(self):
        self.assertEqual(str(self.fornecedor), self.utilizador.username)
    def test_raise_error_ja_eh_fornecedor(self):
        utilizadorTEMP = Utilizador.objects.create(
            email='testfornecedorclassetemp@teste.com',
            first_name='Fornecedor',
            last_name='Caso de Teste',
            nome='Fornecedor Caso de Teste',  # Adicionado manualmente
            username='testfornecedorclassetemp',
            pais='PT',
            cidade='Lisboa',
            freguesia="Penha de França",
            telemovel='+351912345683',
            tipo_utilizador=Utilizador.CONSUMIDOR
        )
        consumidor = Consumidor.objects.create(utilizador=utilizadorTEMP)
        with self.assertRaises(ValueError):
            Fornecedor.objects.create(utilizador=utilizadorTEMP)
            raise ValueError('O utilizador já está associado a um Consumidor.')
    def test_raise_error_user_n_eh_fornecedor(self):
        utilizadorTEMP =         self.utilizador = Utilizador.objects.create(
            email='testfornecedorclassetemp2@teste.com',
            first_name='Fornecedor',
            last_name='Caso de Teste',
            nome='Fornecedor Caso de Teste',  # Adicionado manualmente
            username='testfornecedorclassetemp2',
            pais='PT',
            cidade='Lisboa',
            freguesia="Glória",
            telemovel='+351912345684',
            tipo_utilizador=Utilizador.CONSUMIDOR
        )
        with self.assertRaises(ValueError):
            Consumidor.objects.create(utilizador=utilizadorTEMP)
            raise ValueError('O utilizador não é um fornecedor')