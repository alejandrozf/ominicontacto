# Generated by Django 2.2.7 on 2019-12-04 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0035_auto_20191203_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuacionvigente',
            name='campana',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.Campana'),
        ),
    ]
