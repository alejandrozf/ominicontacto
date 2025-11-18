# Generated manually for adding transcription and resume percentages to Queue
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0115_calificacion_telefono'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='summarize_percentage',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100)
                ],
                verbose_name='Porcentaje a resumir'
            ),
        ),
        migrations.AddField(
            model_name='queue',
            name='transcription_percentage',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100)
                ],
                verbose_name='Porcentaje a transcribir'
            ),
        ),
    ]