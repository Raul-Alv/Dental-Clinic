from django.db import migrations


DIENTES = [
    {
        "codigo": "161227D",
        "display": "Diente molar superior derecho tercero permanente completo",
        "definicion": "",
        "designacion_universal": 1,
        "designacion_iso": 18,
    },
    {
        "codigo": "161262D",
        "display": "Diente molar superior derecho segundo permanente completo",
        "definicion": "",
        "designacion_universal": 2,
        "designacion_iso": 17,
    },
    {
        "codigo": "161010D",
        "display": "Diente molar superior derecho primero permanente completo",
        "definicion": "",
        "designacion_universal": 3,
        "designacion_iso": 16,
    },
    {
        "codigo": "161546D",
        "display": "Diente premolar superior derecho segundo permanente completo",
        "definicion": "",
        "designacion_universal": 4,
        "designacion_iso": 15,
    },
    {
        "codigo": "161607D",
        "display": "Diente premolar superior derecho primero permanente completo",
        "definicion": "",
        "designacion_universal": 5,
        "designacion_iso": 14,
    },
    {
        "codigo": "160840D",
        "display": "Diente canino superior derecho permanente completo",
        "definicion": "",
        "designacion_universal": 6,
        "designacion_iso": 13,
    },
    {
        "codigo": "161941D",
        "display": "Diente incisivo lateral superior derecho permanente completo",
        "definicion": "",
        "designacion_universal": 7,
        "designacion_iso": 12,
    },
    {
        "codigo": "160903D",
        "display": "Diente incisivo central superior derecho permanente completo",
        "definicion": "",
        "designacion_universal": 8,
        "designacion_iso": 11,
    },
    {
        "codigo": "161006D",
        "display": "Diente incisivo central superior izquierdo permanente completo",
        "definicion": "",
        "designacion_universal": 9,
        "designacion_iso": 21,
    },
    {
        "codigo": "161109D",
        "display": "Diente incisivo lateral superior izquierdo permanente completo",
        "definicion": "",
        "designacion_universal": 10,
        "designacion_iso": 22,
    },
    {
        "codigo": "160957D",
        "display": "Diente canino superior izquierdo permanente completo",
        "definicion": "",
        "designacion_universal": 11,
        "designacion_iso": 23,
    },
    {
        "codigo": "161329D",
        "display": "Diente premolar superior izquierdo primero permanente completo",
        "definicion": "",
        "designacion_universal": 12,
        "designacion_iso": 24,
    },
    {
        "codigo": "161178D",
        "display": "Diente premolar superior izquierdo segundo permanente completo",
        "definicion": "",
        "designacion_universal": 13,
        "designacion_iso": 25,
    },
    {
        "codigo": "161132D",
        "display": "Diente molar superior izquierdo primero permanente completo",
        "definicion": "",
        "designacion_universal": 14,
        "designacion_iso": 26,
    },
    {
        "codigo": "161317D",
        "display": "Diente molar superior izquierdo segundo permanente completo",
        "definicion": "",
        "designacion_universal": 15,
        "designacion_iso": 27,
    },
    {
        "codigo": "161454D",
        "display": "Diente molar superior izquierdo tercero permanente completo",
        "definicion": "",
        "designacion_universal": 16,
        "designacion_iso": 28,
    },
    {
        "codigo": "161258D",
        "display": "Diente molar inferior izquierdo tercero permanente completo",
        "definicion": "",
        "designacion_universal": 17,
        "designacion_iso": 38,
    },
    {
        "codigo": "161372D",
        "display": "Diente molar inferior izquierdo segundo permanente completo",
        "definicion": "",
        "designacion_universal": 18,
        "designacion_iso": 37,
    },
    {
        "codigo": "161533D",
        "display": "Diente molar inferior izquierdo primero permanente completo",
        "definicion": "",
        "designacion_universal": 19,
        "designacion_iso": 36,
    },
    {
        "codigo": "161150D",
        "display": "Diente premolar inferior izquierdo segundo permanente completo",
        "definicion": "",
        "designacion_universal": 20,
        "designacion_iso": 35,
    },
    {
        "codigo": "160654D",
        "display": "Diente premolar inferior izquierdo primero permanente completo",
        "definicion": "",
        "designacion_universal": 21,
        "designacion_iso": 34,
    },
    {
        "codigo": "160817D",
        "display": "Diente canino inferior izquierdo permanente completo",
        "definicion": "",
        "designacion_universal": 22,
        "designacion_iso": 33,
    },
    {
        "codigo": "161477D",
        "display": "Diente incisivo lateral inferior izquierdo permanente completo",
        "definicion": "",
        "designacion_universal": 23,
        "designacion_iso": 32,
    },
    {
        "codigo": "161068D",
        "display": "Diente incisivo central inferior izquierdo permanente completo",
        "definicion": "",
        "designacion_universal": 24,
        "designacion_iso": 31,
    },
    {
        "codigo": "161291D",
        "display": "Diente incisivo central inferior derecho permanente completo",
        "definicion": "",
        "designacion_universal": 25,
        "designacion_iso": 41,
    },
    {
        "codigo": "161197D",
        "display": "Diente incisivo lateral inferior derecho permanente completo",
        "definicion": "",
        "designacion_universal": 26,
        "designacion_iso": 42,
    },
    {
        "codigo": "161514D",
        "display": "Diente canino inferior derecho permanente completo",
        "definicion": "",
        "designacion_universal": 27,
        "designacion_iso": 43,
    },
    {
        "codigo": "161496D",
        "display": "Diente premolar inferior derecho primero permanente completo",
        "definicion": "",
        "designacion_universal": 28,
        "designacion_iso": 44,
    },
    {
        "codigo": "161412D",
        "display": "Diente premolar inferior derecho segundo permanente completo",
        "definicion": "",
        "designacion_universal": 29,
        "designacion_iso": 45,
    },
    {
        "codigo": "160770D",
        "display": "Diente molar inferior derecho primero permanente completo",
        "definicion": "",
        "designacion_universal": 30,
        "designacion_iso": 46,
    },
    {
        "codigo": "160704D",
        "display": "Diente molar inferior derecho segundo permanente completo",
        "definicion": "",
        "designacion_universal": 31,
        "designacion_iso": 47,
    },
    {
        "codigo": "161121D",
        "display": "Diente molar inferior derecho tercero permanente completo",
        "definicion": "",
        "designacion_universal": 32,
        "designacion_iso": 48,
    },
]

PROCEDIMIENTOS_CATALOGO = [
    {"codigo": "55162003", "text": " Extracci\u00f3n dental"},
    {"codigo": "65546002", "text": " Extracci\u00f3n de muela del juicio"},
    {
        "codigo": "773273007",
        "text": " Colocaci\u00f3n de corona dental temporal en diente",
    },
    {"codigo": "1264277001", "text": " Tratamiento de conducto radicular"},
    {
        "codigo": "1260193009",
        "text": " Eliminaci\u00f3n de c\u00e1lculo dental con raspador dental",
    },
    {"codigo": "58707002", "text": " Educaci\u00f3n en higiene oral"},
    {"codigo": "63963009", "text": " Profilaxis dental en adultos"},
    {"codigo": "89846007", "text": " Ortopantomograf\u00eda"},
    {
        "codigo": "104791000220103",
        "text": (
            " Aplicaci\u00f3n t\u00f3pica de per\u00f3xido de hidr\u00f3geno en dientes "
            "vitales decolorados mediante f\u00e9rula de blanqueamiento dental"
        ),
    },
]


def seed_reference_catalogs(apps, schema_editor):
    Diente = apps.get_model("clinica", "Diente")
    ProcedimientoCatalogo = apps.get_model("clinica", "ProcedimientoCatalogo")

    for diente in DIENTES:
        codigo = diente["codigo"]
        defaults = {key: value for key, value in diente.items() if key != "codigo"}
        Diente.objects.update_or_create(codigo=codigo, defaults=defaults)

    for procedimiento in PROCEDIMIENTOS_CATALOGO:
        codigo = procedimiento["codigo"]
        defaults = {key: value for key, value in procedimiento.items() if key != "codigo"}
        ProcedimientoCatalogo.objects.update_or_create(codigo=codigo, defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [
        ("clinica", "0013_alter_paciente_genero_alter_paciente_estado_civil"),
    ]

    operations = [
        migrations.RunPython(seed_reference_catalogs, migrations.RunPython.noop),
    ]
