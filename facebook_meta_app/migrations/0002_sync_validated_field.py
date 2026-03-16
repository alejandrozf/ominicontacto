from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_meta_app', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE facebook_meta_app_paginametafacebook "
                        "ADD COLUMN IF NOT EXISTS validated boolean NOT NULL DEFAULT false;"
                    ),
                    reverse_sql=(
                        "ALTER TABLE facebook_meta_app_paginametafacebook "
                        "DROP COLUMN IF EXISTS validated;"
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='paginametafacebook',
                    name='validated',
                    field=models.BooleanField(default=False),
                ),
            ],
        ),
    ]
