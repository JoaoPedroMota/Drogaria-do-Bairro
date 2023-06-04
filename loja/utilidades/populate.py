from ..models import *

Categoria.objects.create(nome="Indefinido(a)", categoria_pai = None)
Categoria.objects.create(nome="Outro(a)", categoria_pai = None)
Categoria.objects.create(nome="Alimentos", categoria_pai = None)
Categoria.objects.create(nome="Frutas e Legumes", categoria_pai=2)
Categoria.objects.create(nome="Frutas", categoria_pai=3)
Categoria.objects.create(nome="Legumes", categoria_pai=3)
Categoria.objects.create(nome="Lacticínios", categoria_pai=2)
Categoria.objects.create(nome="Leite", categoria_pai=6)
Categoria.objects.create(nome="Queijos", categoria_pai=6)
Categoria.objects.create(nome="Iogurtes", categoria_pai=6)
Categoria.objects.create(nome="Doces e Sobremesas", categoria_pai=2)
Categoria.objects.create(nome="Doces", categoria_pai=10)
Categoria.objects.create(nome="Sobremesas", categoria_pai=10)
Categoria.objects.create(nome="Chocolates", categoria_pai=11)
Categoria.objects.create(nome="Gomas", categoria_pai=11)
Categoria.objects.create(nome="Mercearia", categoria_pai=2)
Categoria.objects.create(nome="Conservas", categoria_pai=15)
Categoria.objects.create(nome="Arroz, Massa e Farinha", categoria_pai=15)
Categoria.objects.create(nome="Arroz", categoria_pai=17)
Categoria.objects.create(nome="Massa", categoria_pai=17)
Categoria.objects.create(nome="Farinha", categoria_pai=17)
Categoria.objects.create(nome="Atum", categoria_pai=16)
Categoria.objects.create(nome="Conservas de Peixe", categoria_pai=16)
Categoria.objects.create(nome="Salsichas e Cogumelos", categoria_pai=16)
Categoria.objects.create(nome="Salsichas", categoria_pai=23)
Categoria.objects.create(nome="Cogumelos", categoria_pai=23)
Categoria.objects.create(nome="Patê", categoria_pai=16)
Categoria.objects.create(nome="Feijão, Grão e Milho", categoria_pai=16)
Categoria.objects.create(nome="Feijão", categoria_pai=27)
Categoria.objects.create(nome="Grão", categoria_pai=27)
Categoria.objects.create(nome="Milho", categoria_pai=27)
Categoria.objects.create(nome="Congelados", categoria_pai=2)
Categoria.objects.create(nome="Ervilhas e outros legumes", categoria_pai=31)
Categoria.objects.create(nome="Gelados", categoria_pai=12)
Categoria.objects.create(nome="Sobremesas Tradicionais", categoria_pai=12)
Categoria.objects.create(nome="Doces Conventuais", categoria_pai=11)
Categoria.objects.create(nome="Cereais e Barras", categoria_pai=15)
Categoria.objects.create(nome="Cereais", categoria_pai=36)
Categoria.objects.create(nome="Barras", categoria_pai=36)
Categoria.objects.create(nome="Azeite, Óleo e Vinagre", categoria_pai=15)
Categoria.objects.create(nome="Azeite", categoria_pai=39)
Categoria.objects.create(nome="Óleo", categoria_pai=39)
Categoria.objects.create(nome="Vinagre", categoria_pai=39)
Categoria.objects.create(nome="Café, Chá e Acholatado em Pó", categoria_pai=15)
Categoria.objects.create(nome="Snacks, Batata Frita e Frutos Secos", categoria_pai=15)
Categoria.objects.create(nome="Snacks", categoria_pai=44)
Categoria.objects.create(nome="Batata Frita", categoria_pai=44)
Categoria.objects.create(nome="Molhos e Condimentos", categoria_pai=15)
Categoria.objects.create(nome="Molhos", categoria_pai=47)
Categoria.objects.create(nome="Condimentos", categoria_pai=47)
Categoria.objects.create(nome="Manteiga e Cremes para barrar", categoria_pai=6)
Categoria.objects.create(nome="Manteiga", categoria_pai=50)
Categoria.objects.create(nome="Cremes para Barrar", categoria_pai=50)
Categoria.objects.create(nome="Pizzas Congeladas", categoria_pai=31)
Categoria.objects.create(nome="Douradinhos e Nuggets", categoria_pai=31)
Categoria.objects.create(nome="Douradinhos", categoria_pai=54)
Categoria.objects.create(nome="Nuggets", categoria_pai=54)
Categoria.objects.create(nome="Padaria e Pastelaria", categoria_pai=2)
Categoria.objects.create(nome="Padaria", categoria_pai=57)
Categoria.objects.create(nome="Pastelaria", categoria_pai=57)
Categoria.objects.create(nome="Pão", categoria_pai=57)
Categoria.objects.create(nome="Café", categoria_pai=43)
Categoria.objects.create(nome="Chá", categoria_pai=43)
Categoria.objects.create(nome="Achocolatado em Pó", categoria_pai=43)
Categoria.objects.create(nome="Ervilhas", categoria_pai=32)
Categoria.objects.create(nome="Outros Legumes", categoria_pai=32)
Categoria.objects.create(nome="Frutos Secos", categoria_pai=44)
Categoria.objects.create(nome="Lazer", categoria_pai = None)
Categoria.objects.create(nome="Atividades dentro de Casa", categoria_pai=68)
Categoria.objects.create(nome="Filmes", categoria_pai=69)
Categoria.objects.create(nome="Jogos de Tabuleiro", categoria_pai=69)
Categoria.objects.create(nome="Jogos de Consola", categoria_pai=69)
Categoria.objects.create(nome="Atividades ao Ar Livre", categoria_pai=68)
Categoria.objects.create(nome="Desporto", categoria_pai=73)
Categoria.objects.create(nome="Roupa", categoria_pai = None)
Categoria.objects.create(nome="Roupa de Homem", categoria_pai=75)
Categoria.objects.create(nome="Roupa de Mulher", categoria_pai=75)
Categoria.objects.create(nome="Roupa de Criança", categoria_pai=75)
Categoria.objects.create(nome="Passeio", categoria_pai=73)
Categoria.objects.create(nome="Talho", categoria_pai=2)
Categoria.objects.create(nome="Peixaria", categoria_pai=2)
Categoria.objects.create(nome="Carne Vaca", categoria_pai=80)
Categoria.objects.create(nome="Carne Porco", categoria_pai=80)
Categoria.objects.create(nome="Carne Frango", categoria_pai=80)
Categoria.objects.create(nome="Carne de Borrego", categoria_pai=80)
Categoria.objects.create(nome="Carne de Caça", categoria_pai=80)
Categoria.objects.create(nome="Carne de Perú", categoria_pai=80)
Categoria.objects.create(nome="Outras Aves", categoria_pai=80)
Categoria.objects.create(nome="Bacalhau", categoria_pai=81)
Categoria.objects.create(nome="Carne de Cabrito", categoria_pai=80)
Categoria.objects.create(nome="Peixe Fresco", categoria_pai=81)
Categoria.objects.create(nome="Peixe Congelado", categoria_pai=81)
Categoria.objects.create(nome="Polvo, Lulas e Choco", categoria_pai=81)
Categoria.objects.create(nome="Polvo", categoria_pai=93)
Categoria.objects.create(nome="Lulas", categoria_pai=93)
Categoria.objects.create(nome="Choco", categoria_pai=93)
Categoria.objects.create(nome="Camarão", categoria_pai=81)
Categoria.objects.create(nome="Marisco", categoria_pai=81)
Categoria.objects.create(nome="Filetes, Lombos e Postas", categoria_pai=81)
Categoria.objects.create(nome="Carne Congelada", categoria_pai=80)