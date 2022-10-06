# Generated by Django 2.2.7 on 2022-08-10 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0097_historicalrespuestaformulario_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutenticacionSitioExterno',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128, unique=True)),
                ('url', models.URLField(max_length=250)),
                ('username', models.CharField(max_length=128)),
                ('password', models.CharField(max_length=128)),
                ('campo_token', models.CharField(default='token', max_length=128)),
                ('duracion', models.PositiveIntegerField()),
                ('campo_duracion', models.CharField(blank=True, max_length=128)),
                ('ssl_estricto', models.BooleanField(default=True)),
                ('token', models.TextField(blank=True, null=True)),
                ('expiracion_token', models.DateTimeField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='sitioexterno',
            name='autenticacion',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='sitios_externos', to='ominicontacto_app.AutenticacionSitioExterno'),
        ),
    ]