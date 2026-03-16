from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_meta_app', '0002_sync_validated_field'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE facebook_meta_app_configuracionmetafacebookcampana "
                        "ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;"
                    ),
                    reverse_sql=(
                        "ALTER TABLE facebook_meta_app_configuracionmetafacebookcampana "
                        "DROP COLUMN IF EXISTS is_active;"
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='configuracionmetafacebookcampana',
                    name='is_active',
                    field=models.BooleanField(default=True),
                ),
            ],
        ),
    ]
