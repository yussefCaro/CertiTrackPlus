# Generated by Django 5.1.5 on 2025-05-24 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ejecucion_auditoria', '0004_alter_ejecucionrequisito_aspecto_mejora_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ejecucionrequisito',
            name='aspecto_mejora',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='ejecucionrequisito',
            name='cumple',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='ejecucionrequisito',
            name='no_aplica',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='ejecucionrequisito',
            name='no_cumple',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='ejecucionrequisito',
            name='subsanado',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='noconformidad',
            name='subsanado',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
