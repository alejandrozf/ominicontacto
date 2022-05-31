# Generated by Django 2.2.7 on 2022-04-18 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0092_conjuntos_de_pausas_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='campana',
            name='control_de_duplicados',
            field=models.PositiveIntegerField(choices=[(1, 'Evitar duplicados'), (2, 'Permitir duplicados')], default=2),
        ),
    ]