# Generated by Django 3.2.19 on 2024-02-07 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuracionwhatsappcampana',
            name='grupo_plantilla_whatsapp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='configuracionwhatsapp', to='whatsapp_app.grupoplantillamensaje'),
        ),
    ]