# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-07-31 19:30
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import ominicontacto_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_agente', models.BooleanField(default=False)),
                ('is_supervisor', models.BooleanField(default=False)),
                ('last_session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('borrado', models.BooleanField(default=False, editable=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ActuacionVigente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domingo', models.BooleanField()),
                ('lunes', models.BooleanField()),
                ('martes', models.BooleanField()),
                ('miercoles', models.BooleanField()),
                ('jueves', models.BooleanField()),
                ('viernes', models.BooleanField()),
                ('sabado', models.BooleanField()),
                ('hora_desde', models.TimeField()),
                ('hora_hasta', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('es_personal', models.BooleanField()),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('es_smart', models.BooleanField()),
                ('medio_comunicacion', models.PositiveIntegerField(choices=[(1, 'SMS'), (2, 'LLAMADA'), (3, 'EMAIL')])),
                ('telefono', models.CharField(blank=True, max_length=128, null=True)),
                ('email', models.CharField(blank=True, max_length=128, null=True)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AgendaContacto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('tipo_agenda', models.PositiveIntegerField(choices=[(1, 'PERSONAL'), (2, 'GLOBAL')])),
                ('observaciones', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AgenteEnContacto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agente_id', models.IntegerField()),
                ('contacto_id', models.IntegerField()),
                ('datos_contacto', models.TextField()),
                ('telefono_contacto', models.CharField(max_length=128)),
                ('campana_id', models.IntegerField()),
                ('estado', models.PositiveIntegerField(choices=[(0, 'INICIAL'), (1, 'ENTREGADO'), (2, 'FINALIZADO')])),
                ('modificado', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AgenteProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sip_extension', models.IntegerField(unique=True)),
                ('sip_password', models.CharField(blank=True, max_length=128, null=True)),
                ('estado', models.PositiveIntegerField(choices=[(1, 'OFFLINE'), (2, 'ONLINE'), (3, 'PAUSA')], default=1)),
                ('is_inactive', models.BooleanField(default=False)),
                ('borrado', models.BooleanField(default=False, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='ArchivoDeAudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=100, unique=True)),
                ('audio_original', models.FileField(blank=True, null=True, upload_to=ominicontacto_app.models.upload_to_audio_original)),
                ('audio_asterisk', models.FileField(blank=True, null=True, upload_to=ominicontacto_app.models.upload_to_audio_asterisk)),
                ('borrado', models.BooleanField(default=False, editable=False)),
            ],
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Backlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128)),
                ('fecha_alta', models.DateTimeField(auto_now_add=True)),
                ('archivo_importacion', models.FileField(max_length=256, upload_to=ominicontacto_app.models.upload_to)),
                ('nombre_archivo_importacion', models.CharField(max_length=256)),
                ('sin_definir', models.BooleanField(default=True)),
                ('cantidad_contactos', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='BaseDatosContacto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128)),
                ('fecha_alta', models.DateTimeField(auto_now_add=True)),
                ('archivo_importacion', models.FileField(max_length=256, upload_to=ominicontacto_app.models.upload_to)),
                ('nombre_archivo_importacion', models.CharField(max_length=256)),
                ('metadata', models.TextField(blank=True, null=True)),
                ('sin_definir', models.BooleanField(default=True)),
                ('cantidad_contactos', models.PositiveIntegerField(default=0)),
                ('estado', models.PositiveIntegerField(choices=[(0, 'En Definici\xf3n'), (1, 'Definida'), (2, 'En Depuracion'), (3, 'Depurada'), (4, 'Definida en actualizacion')], default=0)),
                ('oculto', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CalificacionCliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('es_venta', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('agendado', models.BooleanField(default=False)),
                ('es_calificacion_manual', models.BooleanField(default=False)),
                ('agente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones', to='ominicontacto_app.AgenteProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Campana',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.PositiveIntegerField(choices=[(2, 'Activa'), (3, 'Finalizada'), (4, 'Borrada'), (5, 'Pausada'), (6, 'Inactiva'), (8, 'Template Activo'), (9, 'Template Borrado')], default=6)),
                ('nombre', models.CharField(max_length=128, unique=True)),
                ('fecha_inicio', models.DateField(blank=True, null=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('oculto', models.BooleanField(default=False)),
                ('gestion', models.CharField(default='Venta', max_length=128)),
                ('campaign_id_wombat', models.IntegerField(blank=True, null=True)),
                ('type', models.PositiveIntegerField(choices=[(3, 'Entrante'), (2, 'Dialer'), (1, 'Manual'), (4, 'Preview')])),
                ('tipo_interaccion', models.PositiveIntegerField(choices=[(1, 'Formulario'), (2, 'Url externa')], default=1)),
                ('es_template', models.BooleanField(default=False)),
                ('nombre_template', models.CharField(blank=True, max_length=128, null=True)),
                ('es_manual', models.BooleanField(default=False)),
                ('objetivo', models.PositiveIntegerField(default=0)),
                ('tiempo_desconexion', models.PositiveIntegerField(default=0)),
                ('bd_contacto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campanas', to='ominicontacto_app.BaseDatosContacto')),
            ],
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_chat', models.DateTimeField(auto_now=True)),
                ('agente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatsagente', to='ominicontacto_app.AgenteProfile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatsusuario', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contacto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(max_length=128)),
                ('datos', models.TextField()),
                ('bd_contacto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contactos', to='ominicontacto_app.BaseDatosContacto')),
            ],
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ContactoBacklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(max_length=128)),
                ('back_list', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contactosbacklist', to='ominicontacto_app.Backlist')),
            ],
        ),
        migrations.CreateModel(
            name='DuracionDeLlamada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_telefono', models.CharField(max_length=20)),
                ('fecha_hora_llamada', models.DateTimeField(auto_now=True)),
                ('tipo_llamada', models.PositiveIntegerField(choices=[(4, 'PREVIEW'), (2, 'DIALER'), (3, 'INBOUND'), (1, 'MANUAL')])),
                ('duracion', models.TimeField()),
                ('agente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='llamadas', to='ominicontacto_app.AgenteProfile')),
            ],
        ),
        migrations.CreateModel(
            name='FieldFormulario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_campo', models.CharField(max_length=64)),
                ('orden', models.PositiveIntegerField()),
                ('tipo', models.PositiveIntegerField(choices=[(1, 'Texto'), (2, 'Fecha'), (3, 'Lista'), (4, 'Caja de Texto de Area')])),
                ('values_select', models.TextField(blank=True, null=True)),
                ('is_required', models.BooleanField()),
            ],
            options={
                'ordering': ['orden'],
            },
        ),
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=64)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Grabacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
                ('tipo_llamada', models.PositiveIntegerField(choices=[(2, 'DIALER'), (3, 'INBOUND'), (1, 'MANUAL'), (4, 'PREVIEW')])),
                ('id_cliente', models.CharField(max_length=255)),
                ('tel_cliente', models.CharField(max_length=255)),
                ('grabacion', models.CharField(max_length=255)),
                ('sip_agente', models.IntegerField()),
                ('uid', models.CharField(blank=True, max_length=45, null=True)),
                ('duracion', models.IntegerField(default=0)),
                ('campana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grabaciones', to='ominicontacto_app.Campana')),
            ],
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='GrabacionMarca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=45)),
                ('descripcion', models.TextField()),
            ],
            options={
                'db_table': 'ominicontacto_app_grabacion_marca',
            },
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20)),
                ('auto_attend_ics', models.BooleanField(default=False)),
                ('auto_attend_inbound', models.BooleanField(default=False)),
                ('auto_attend_dialer', models.BooleanField(default=False)),
                ('auto_pause', models.BooleanField(default=True)),
                ('auto_unpause', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalCalificacionCliente',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('es_venta', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(blank=True, editable=False)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('agendado', models.BooleanField(default=False)),
                ('es_calificacion_manual', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('agente', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ominicontacto_app.AgenteProfile')),
                ('contacto', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ominicontacto_app.Contacto')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical calificacion cliente',
            },
        ),
        migrations.CreateModel(
            name='MensajeChat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('fecha_hora', models.DateTimeField(auto_now=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajeschat', to='ominicontacto_app.Chat')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatssender', to=settings.AUTH_USER_MODEL)),
                ('to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatsto', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MensajeEnviado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remitente', models.CharField(max_length=20)),
                ('destinatario', models.CharField(max_length=20)),
                ('timestamp', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('result', models.IntegerField(blank=True, null=True)),
                ('agente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.AgenteProfile')),
            ],
            options={
                'db_table': 'mensaje_enviado',
            },
        ),
        migrations.CreateModel(
            name='MensajeRecibido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remitente', models.CharField(max_length=20)),
                ('destinatario', models.CharField(max_length=20)),
                ('timestamp', models.CharField(max_length=255)),
                ('timezone', models.IntegerField()),
                ('encoding', models.IntegerField()),
                ('content', models.TextField()),
                ('es_leido', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'mensaje_recibido',
            },
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='MetadataCliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metadata', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('agente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadataagente', to='ominicontacto_app.AgenteProfile')),
                ('campana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadatacliente', to='ominicontacto_app.Campana')),
                ('contacto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.Contacto')),
            ],
        ),
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='NombreCalificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='OpcionCalificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.IntegerField(choices=[(1, 'Gesti\xf3n'), (0, 'Sin acci\xf3n'), (2, 'Agenda')], default=0)),
                ('nombre', models.CharField(max_length=50)),
                ('campana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opciones_calificacion', to='ominicontacto_app.Campana')),
            ],
        ),
        migrations.CreateModel(
            name='ParametroExtraParaWebform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parametro', models.CharField(max_length=32)),
                ('columna', models.CharField(max_length=32)),
                ('campana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parametros_extra_para_webform', to='ominicontacto_app.Campana')),
            ],
        ),
        migrations.CreateModel(
            name='Pausa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20, unique=True)),
                ('tipo', models.CharField(choices=[('P', 'Productiva'), ('R', 'Recreativa')], default='P', max_length=1)),
                ('eliminada', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('name', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('timeout', models.BigIntegerField(blank=True, null=True, verbose_name='Tiempo de Ring')),
                ('retry', models.BigIntegerField(blank=True, null=True, verbose_name='Tiempo de Reintento')),
                ('maxlen', models.BigIntegerField(verbose_name='Cantidad Max de llamadas')),
                ('wrapuptime', models.BigIntegerField(verbose_name='Tiempo de descanso entre llamadas')),
                ('servicelevel', models.BigIntegerField(verbose_name='Nivel de Servicio')),
                ('strategy', models.CharField(choices=[('ringall', 'Ringall'), ('rrordered', 'Rrordered'), ('leastrecent', 'Leastrecent'), ('fewestcalls', 'Fewestcalls'), ('random', 'Random'), ('rrmemory', 'Rremory')], max_length=128, verbose_name='Estrategia de distribucion')),
                ('eventmemberstatus', models.BooleanField()),
                ('eventwhencalled', models.BooleanField()),
                ('weight', models.BigIntegerField(verbose_name='Importancia de campa\xf1a')),
                ('ringinuse', models.BooleanField()),
                ('setinterfacevar', models.BooleanField()),
                ('wait', models.PositiveIntegerField(verbose_name='Tiempo de espera en cola')),
                ('auto_grabacion', models.BooleanField(default=False, verbose_name='Grabar llamados')),
                ('detectar_contestadores', models.BooleanField(default=False)),
                ('ep_id_wombat', models.IntegerField(blank=True, null=True)),
                ('announce', models.CharField(blank=True, max_length=128, null=True)),
                ('announce_frequency', models.BigIntegerField(blank=True, null=True)),
                ('initial_predictive_model', models.BooleanField(default=False)),
                ('initial_boost_factor', models.DecimalField(blank=True, decimal_places=1, default=1.0, max_digits=3, null=True)),
                ('musiconhold', models.CharField(blank=True, max_length=128, null=True)),
                ('context', models.CharField(blank=True, max_length=128, null=True)),
                ('monitor_join', models.NullBooleanField()),
                ('monitor_format', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_youarenext', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_thereare', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_callswaiting', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_holdtime', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_minutes', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_seconds', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_lessthan', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_thankyou', models.CharField(blank=True, max_length=128, null=True)),
                ('queue_reporthold', models.CharField(blank=True, max_length=128, null=True)),
                ('announce_round_seconds', models.BigIntegerField(blank=True, null=True)),
                ('announce_holdtime', models.CharField(blank=True, max_length=128, null=True)),
                ('joinempty', models.CharField(blank=True, max_length=128, null=True)),
                ('leavewhenempty', models.CharField(blank=True, max_length=128, null=True)),
                ('reportholdtime', models.NullBooleanField()),
                ('memberdelay', models.BigIntegerField(blank=True, null=True)),
                ('timeoutrestart', models.NullBooleanField()),
                ('audio_de_ingreso', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='queues_ingreso', to='ominicontacto_app.ArchivoDeAudio')),
                ('audio_para_contestadores', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='queues_contestadores', to='ominicontacto_app.ArchivoDeAudio')),
                ('audios', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='queues_anuncio_periodico', to='ominicontacto_app.ArchivoDeAudio')),
                ('campana', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='queue_campana', to='ominicontacto_app.Campana')),
            ],
            options={
                'db_table': 'queue_table',
            },
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='QueueMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membername', models.CharField(max_length=128)),
                ('interface', models.CharField(max_length=128)),
                ('penalty', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9')])),
                ('paused', models.IntegerField()),
                ('id_campana', models.CharField(max_length=128)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campana_member', to='ominicontacto_app.AgenteProfile')),
                ('queue_name', models.ForeignKey(db_column='queue_name', on_delete=django.db.models.deletion.CASCADE, related_name='queuemember', to='ominicontacto_app.Queue')),
            ],
            options={
                'db_table': 'queue_member_table',
            },
            managers=[
                ('objects_default', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ReglasIncidencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.PositiveIntegerField(choices=[(1, 'Ocupado'), (2, 'Contestador'), (3, 'No atendido'), (4, 'Rechazado'), (5, 'Timeout')])),
                ('estado_personalizado', models.CharField(blank=True, max_length=128, null=True)),
                ('intento_max', models.IntegerField()),
                ('reintentar_tarde', models.IntegerField()),
                ('en_modo', models.PositiveIntegerField(choices=[(1, 'FIXED'), (2, 'MULT')], default=2)),
                ('campana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reglas_incidencia', to='ominicontacto_app.Campana')),
            ],
        ),
        migrations.CreateModel(
            name='SitioExterno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=128)),
                ('url', models.CharField(max_length=256)),
                ('oculto', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SupervisorProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sip_extension', models.IntegerField(unique=True)),
                ('sip_password', models.CharField(blank=True, max_length=128, null=True)),
                ('is_administrador', models.BooleanField(default=False)),
                ('is_customer', models.BooleanField(default=False)),
                ('borrado', models.BooleanField(default=False, editable=False)),
                ('timestamp', models.CharField(blank=True, max_length=64, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserApiCrm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=64, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='queue',
            name='members',
            field=models.ManyToManyField(through='ominicontacto_app.QueueMember', to='ominicontacto_app.AgenteProfile'),
        ),
        migrations.AddField(
            model_name='historicalcalificacioncliente',
            name='opcion_calificacion',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ominicontacto_app.OpcionCalificacion'),
        ),
        migrations.AddField(
            model_name='fieldformulario',
            name='formulario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campos', to='ominicontacto_app.Formulario'),
        ),
        migrations.AddField(
            model_name='campana',
            name='formulario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.Formulario'),
        ),
        migrations.AddField(
            model_name='campana',
            name='reported_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='campana',
            name='sitio_externo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.SitioExterno'),
        ),
        migrations.AddField(
            model_name='campana',
            name='supervisors',
            field=models.ManyToManyField(related_name='campanasupervisors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='calificacioncliente',
            name='contacto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.Contacto'),
        ),
        migrations.AddField(
            model_name='calificacioncliente',
            name='opcion_calificacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones_cliente', to='ominicontacto_app.OpcionCalificacion'),
        ),
        migrations.AddField(
            model_name='agenteprofile',
            name='grupo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agentes', to='ominicontacto_app.Grupo'),
        ),
        migrations.AddField(
            model_name='agenteprofile',
            name='modulos',
            field=models.ManyToManyField(to='ominicontacto_app.Modulo'),
        ),
        migrations.AddField(
            model_name='agenteprofile',
            name='reported_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reportedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agenteprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agendacontacto',
            name='agente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agendacontacto', to='ominicontacto_app.AgenteProfile'),
        ),
        migrations.AddField(
            model_name='agendacontacto',
            name='campana',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agendas', to='ominicontacto_app.Campana'),
        ),
        migrations.AddField(
            model_name='agendacontacto',
            name='contacto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.Contacto'),
        ),
        migrations.AddField(
            model_name='agenda',
            name='agente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventos', to='ominicontacto_app.AgenteProfile'),
        ),
        migrations.AddField(
            model_name='actuacionvigente',
            name='campana',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ominicontacto_app.Campana'),
        ),
        migrations.AlterUniqueTogether(
            name='queuemember',
            unique_together=set([('queue_name', 'member')]),
        ),
        migrations.AlterUniqueTogether(
            name='fieldformulario',
            unique_together=set([('orden', 'formulario')]),
        ),
    ]
