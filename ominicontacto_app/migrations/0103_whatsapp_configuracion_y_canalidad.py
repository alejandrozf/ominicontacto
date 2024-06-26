# Generated by Django 3.2.19 on 2023-12-28 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0102_autenticacion_externa_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='calificacioncliente',
            name='canalidad',
            field=models.PositiveIntegerField(choices=[(0, 'Teléfono'), (1, 'Whatsapp')],
                                              default=0),
        ),
        migrations.AddField(
            model_name='campana',
            name='whatsapp_habilitado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='grupo',
            name='whatsapp_habilitado',
            field=models.BooleanField(default=False,
                                      verbose_name='Permiso de uso de la canalidad WhatsApp'),
        ),
        migrations.AddField(
            model_name='historicalcalificacioncliente',
            name='canalidad',
            field=models.PositiveIntegerField(choices=[(0, 'Teléfono'), (1, 'Whatsapp')],
                                              default=0),
        ),
    ]
