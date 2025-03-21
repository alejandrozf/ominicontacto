# Generated by Django 3.2.19 on 2024-11-08 09:53

from django.db import migrations, models


def forwards_code(apps, schema_editor):
    AgenteProfile = apps.get_model("ominicontacto_app", "AgenteProfile")
    ContentType = apps.get_model("contenttypes", "ContentType")
    DestinoEntrante = apps.get_model("configuracion_telefonia_app", "DestinoEntrante")
    DestinoEntrante.AGENTE = 11
    agente_profiles = AgenteProfile.objects.select_related("user").filter(
        is_inactive=False,
        borrado=False,
        user__borrado=False,
    )
    content_type = ContentType.objects.get_for_model(AgenteProfile)
    for agente_profile in agente_profiles:
        DestinoEntrante.objects.create(
            nombre=agente_profile.user.username,
            tipo=DestinoEntrante.AGENTE,
            content_type=content_type,
            object_id=agente_profile.id
        )


def reverse_code(apps, schema_editor):
    DestinoEntrante = apps.get_model("configuracion_telefonia_app", "DestinoEntrante")
    DestinoEntrante.AGENTE = 11
    DestinoEntrante.objects.filter(tipo=DestinoEntrante.AGENTE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0107_add_tipo_numero_fieldformulario'),
        ('configuracion_telefonia_app', '0020_patrondediscado_regex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destinoentrante',
            name='tipo',
            field=models.PositiveIntegerField(choices=[(1, 'Campaña entrante'), (2, 'Validación de fecha/hora'), (3, 'IVR'), (5, 'HangUp'), (9, 'Identificador cliente'), (7, 'Destino personalizado'), (10, 'Menú Interactivo de Whatsapp'), (11, 'Agente')]),
        ),
        migrations.RunPython(forwards_code, reverse_code),
    ]
