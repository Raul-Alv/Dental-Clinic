from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clinica", "0012_alter_procedimiento_descripcion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paciente",
            name="genero",
            field=models.CharField(
                choices=[
                    ("male", "Masculino"),
                    ("female", "Femenino"),
                    ("other", "Otro"),
                    ("unknown", "Desconocido"),
                ],
                default="unknown",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="paciente",
            name="estado_civil",
            field=models.CharField(
                choices=[
                    ("A", "Anulado"),
                    ("D", "Divorciado"),
                    ("M", "Casado"),
                    ("U", "Soltero"),
                    ("W", "Viudo/a"),
                    ("UNK", "Desconocido"),
                ],
                default="UNK",
                max_length=10,
            ),
        ),
    ]
