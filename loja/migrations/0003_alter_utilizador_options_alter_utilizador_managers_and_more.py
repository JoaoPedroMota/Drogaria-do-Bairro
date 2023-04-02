# Generated by Django 4.1.7 on 2023-04-02 02:28

import django.contrib.auth.validators
from django.db import migrations, models
import loja.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0002_alter_utilizador_options_utilizador_cidade_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='utilizador',
            options={'ordering': ['username', '-created', '-updated'], 'verbose_name': 'Utilizador', 'verbose_name_plural': 'Utilizadores'},
        ),
        migrations.AlterModelManagers(
            name='utilizador',
            managers=[
                ('objects', loja.models.CustomUserManager()),
            ],
        ),
        migrations.AddField(
            model_name='utilizador',
            name='is_admin',
            field=models.BooleanField(default=False, help_text='Designa se este utilizador tem permissão para realizar ações de administrador.'),
        ),
        migrations.AddField(
            model_name='utilizador',
            name='username_l',
            field=models.CharField(error_messages={'unique': 'Já existe um utilizador com esse nome de utilizador.'}, help_text='Obrigatório. 20 caracteres ou menos. Apenas letras, dígitos e @/./+/-/_ são permitidos.', max_length=20, null=True, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()]),
        ),
        migrations.AlterField(
            model_name='utilizador',
            name='email',
            field=models.EmailField(error_messages={'unique': 'Já existe um utilizador com esse e-mail.'}, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='utilizador',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designa se este utilizador pode aceder à área de administração do site.'),
        ),
        migrations.AlterField(
            model_name='utilizador',
            name='telemovel',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, error_messages={'unique': 'Já existe um utilizador com esse número de telefone.'}, max_length=128, null=True, region=None, unique=True),
        ),
    ]
