# Generated by Django 3.2.19 on 2024-02-20 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp_app', '0003_conversacionwhatsapp_client_alias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensajewhatsapp',
            name='conversation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='whatsapp_app.conversacionwhatsapp'),
        ),
    ]