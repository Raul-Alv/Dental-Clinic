# Generated by Django 5.2 on 2025-06-10 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clinica', '0005_remove_paciente_direccion_paciente_calle_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paciente',
            old_name='coidad',
            new_name='ciudad',
        ),
    ]
