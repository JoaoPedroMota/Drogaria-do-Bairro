from django.db import models
from .models import ProdutoUnidadeProducao

class Imagem(models.Model):
    produto = models.ForeignKey(ProdutoUnidadeProducao, on_delete=models.CASCADE, related_name='imagens_produto')

    imagem = models.ImageField(upload_to='produtos/imagens/')

    def __str__(self):
        return f"Imagem do produto "