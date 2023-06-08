# Generated by Django 4.1.7 on 2023-06-08 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0006_rename_produto_encomenda_produtosencomendadosveiculos_produto_encomendado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veiculo',
            name='estado_veiculo',
            field=models.CharField(choices=[('D', 'Disponível'), ('C', 'A carregar'), ('E', 'A entregar'), ('I/M', 'Indisponível/Manutenção'), ('R', 'Regresso')], default='D', max_length=5, null=True),
        ),
    ]