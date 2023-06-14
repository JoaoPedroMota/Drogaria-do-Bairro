# Generated by Django 4.1.7 on 2023-06-14 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0003_alter_encomenda_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtosencomenda',
            name='estado',
            field=models.CharField(choices=[('Em processamento', 'Em processamento'), ('A sair da Unidade da Producao', 'A sair da Unidade da Producao'), ('Enviado', 'Enviado'), ('A chegar', 'A chegar'), ('Entregue', 'Entregue'), ('Cancelado', 'Cancelado')], default='Em processamento', max_length=30),
        ),
    ]
