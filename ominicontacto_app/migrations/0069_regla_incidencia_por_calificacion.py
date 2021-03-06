# Generated by Django 2.2.7 on 2020-12-18 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0068_videocall_habilitada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reglasincidencia',
            name='en_modo',
            field=models.PositiveIntegerField(choices=[(1, 'FIXED'), (2, 'MULT')], default=1),
        ),
        migrations.CreateModel(
            name='ReglaIncidenciaPorCalificacion',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intento_max', models.IntegerField(verbose_name='Cantidad de reintentos')),
                ('reintentar_tarde', models.IntegerField(
                    verbose_name='Tiempo entre reintentos (seg)')),
                ('en_modo', models.PositiveIntegerField(
                    choices=[(1, 'FIXED'), (2, 'MULT')], default=1, verbose_name='Modo')),
                ('opcion_calificacion', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='regla_incidencia',
                    to='ominicontacto_app.OpcionCalificacion',
                    verbose_name='Opción de calificación')),
            ],
            options={
                'verbose_name': 'Regla de incidencia por calificación',
            },
        ),
    ]
