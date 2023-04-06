# Generated by Django 4.1.7 on 2023-04-04 23:15

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0004_remove_utilizador_morada'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnidadeProducao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, null=True)),
                ('pais', django_countries.fields.CountryField(default='PT', max_length=2, null=True)),
                ('cidade', models.CharField(max_length=100, null=True)),
                ('morada', models.CharField(max_length=200, null=True)),
                ('tipo_unidade', models.CharField(choices=[('A', 'Armazém'), ('Q', 'Quinta'), ('MM', 'Mini-mercado'), ('SM', 'Supermercado'), ('HM', 'Hipermercado'), ('LR', 'Loja de Rua'), ('LCC', 'Loja Centro Comercial'), ('O', 'Outro')], default='', max_length=5, null=True)),
                ('fornecedor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.fornecedor')),
            ],
        ),
        migrations.AlterField(
            model_name='utilizador',
            name='pais',
            field=django_countries.fields.CountryField(default='PT', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='utilizador',
            name='telemovel',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, error_messages={'unique': 'Já existe um utilizador com esse número de telefone.'}, help_text='O País default para os números de telemóvel é Portugal(+351). Se o seu número for de um país diferente tem de adicionar o identificador desse país.', max_length=128, null=True, region=None, unique=True),
        ),
        migrations.CreateModel(
            name='Veiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, null=True)),
                ('tipo_veiculo', models.CharField(choices=[('C', 'Carro'), ('E', 'Estafeta a pé'), ('M', 'Mota'), ('B', 'Bicicleta'), ('T', 'Trotineta'), ('CR', 'Carrinha'), ('CM', 'Camião')], default='', max_length=5, null=True)),
                ('estado_veiculo', models.CharField(choices=[('D', 'Disponível'), ('A-C', 'A caminho'), ('E', 'A entregar'), ('I/M', 'Indisponível/Manutenção'), ('R', 'Regresso'), ('W', 'À espera')], default='D', max_length=5, null=True)),
                ('unidadeProducao', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.unidadeproducao')),
            ],
        ),
    ]