# Generated by Django 4.1.7 on 2023-06-13 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0002_alter_produtoscarrinho_produto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encomenda',
            name='estado',
            field=models.CharField(choices=[('Em processamento', 'Em processamento'), ('Entregue', 'Entregue'), ('Cancelado', 'Cancelado')], default='Em processamento', max_length=20),
        ),
    ]
