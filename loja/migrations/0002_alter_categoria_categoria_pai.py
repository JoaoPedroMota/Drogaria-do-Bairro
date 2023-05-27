# Generated by Django 4.1.7 on 2023-05-24 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='categoria_pai',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categorias_filhas', to='loja.categoria'),
        ),
    ]
