# Generated by Django 3.2.19 on 2025-03-27 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp_app', '0013_alter_maxlength_menuinteractivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linea',
            name='destino',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lineas', to='configuracion_telefonia_app.destinoentrante'),
        ),
        migrations.AlterField(
            model_name='linea',
            name='horario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lineas', to='configuracion_telefonia_app.grupohorario'),
        ),
        migrations.AlterField(
            model_name='linea',
            name='mensaje_bienvenida',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='linea_mensaje_bienvenida', to='whatsapp_app.plantillamensaje'),
        ),
        migrations.AlterField(
            model_name='linea',
            name='mensaje_despedida',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='linea_mensaje_despedida', to='whatsapp_app.plantillamensaje'),
        ),
        migrations.AlterField(
            model_name='linea',
            name='mensaje_fueradehora',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='linea_mensaje_fueradehora', to='whatsapp_app.plantillamensaje'),
        ),
        migrations.AlterField(
            model_name='linea',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lineas', to='whatsapp_app.configuracionproveedor'),
        ),
    ]
