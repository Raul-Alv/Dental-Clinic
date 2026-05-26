import io
import zipfile

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.utils.text import slugify
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

from .models import Diente, Paciente, Practicante, Procedimiento, ProcedimientoCatalogo
from .shex_fhir import (
    FHIR,
    PATIENT_SHAPE,
    PRACTITIONER_SHAPE,
    PROCEDURE_SHAPE,
    build_fhir_schema,
    detect_focus_nodes,
    validate_uploaded_schema,
)


FHIR_VALUE = FHIR["value"]

PRACTITIONER_TO_FHIR_GENDER = {
    "M": "male",
    "F": "female",
    "O": "other",
}

FHIR_TO_PRACTITIONER_GENDER = {
    "male": "M",
    "female": "F",
    "other": "O",
    "unknown": "O",
}


def _literal_to_python(value, default=None):
    if value is None:
        return default
    return value.toPython() if hasattr(value, "toPython") else value


def _add_wrapped_literal(graph, subject, predicate, value, datatype=None):
    wrapper = BNode()
    graph.add((subject, predicate, wrapper))

    literal = Literal(value, datatype=datatype) if datatype else Literal(value)
    graph.add((wrapper, FHIR_VALUE, literal))
    return wrapper


def _wrapped_value(graph, subject, predicate, default=None):
    if subject is None:
        return default
    wrapper = graph.value(subject, predicate)
    if wrapper is None:
        return default
    return _literal_to_python(graph.value(wrapper, FHIR_VALUE), default)


def _telecom_value(graph, subject, telecom_predicate, system_name="phone"):
    for telecom in graph.objects(subject, telecom_predicate):
        system = _wrapped_value(graph, telecom, FHIR["ContactPoint.system"])
        if system == system_name:
            return _wrapped_value(graph, telecom, FHIR["ContactPoint.value"], "")
    return ""


def _reference_value(graph, subject, predicate):
    if subject is None:
        return None
    wrapper = graph.value(subject, predicate)
    if wrapper is None:
        return None
    reference = graph.value(wrapper, FHIR["Reference.reference"])
    if reference is None:
        return None
    return _literal_to_python(graph.value(reference, FHIR_VALUE))


def _resource_identifier(value):
    if value is None:
        return None

    raw_value = str(value).rstrip("/")
    if not raw_value:
        return None

    return raw_value.split("/")[-1]


def _numeric_identifier(value):
    identifier = _resource_identifier(value)
    if identifier and identifier.isdigit():
        return int(identifier)
    return None


def _absolute_reference(value):
    raw_value = str(value or "").strip()
    return raw_value if "://" in raw_value else None


def _read_uploaded_text(uploaded_file, label):
    raw_content = uploaded_file.read()

    if isinstance(raw_content, str):
        return raw_content

    try:
        return raw_content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"El archivo {label} debe estar codificado en UTF-8.") from exc


def _safe_filename(base_name):
    normalized = slugify(base_name) or "exportacion-fhir"
    return normalized


def _new_graph():
    graph = Graph()
    graph.bind("fhir", FHIR)
    return graph


def _export_bundle(graph, base_name, schema_text):
    bundle = io.BytesIO()
    safe_base_name = _safe_filename(base_name)

    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{safe_base_name}.ttl", graph.serialize(format="turtle"))
        archive.writestr(f"{safe_base_name}.shex", schema_text)

    response = HttpResponse(bundle.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{safe_base_name}.zip"'
    return response


def _graph_with_resources(*, pacientes=None, practicantes=None, procedimientos=None):
    graph = _new_graph()

    for paciente in pacientes or []:
        patient_rdf_graph(graph, paciente)

    for practicante in practicantes or []:
        practitioner_rdf_graph(graph, practicante)

    for procedimiento in procedimientos or []:
        procedimiento_rdf_graph(graph, procedimiento)

    return graph


def export_all_rdf(request):
    pacientes = list(Paciente.objects.all())
    practicantes = list(Practicante.objects.all())
    procedimientos = list(
        Procedimiento.objects.select_related("codigo", "paciente", "practicante", "diente").all()
    )
    graph = _graph_with_resources(
        pacientes=pacientes,
        practicantes=practicantes,
        procedimientos=procedimientos,
    )
    schema = build_fhir_schema(
        include_patients=True,
        include_practitioners=True,
        include_procedures=True,
    )
    return _export_bundle(graph, "exportacion-completa-fhir", schema)


def export_patient_rdf(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    graph = _graph_with_resources(pacientes=[paciente])
    schema = build_fhir_schema(include_patients=True)
    return _export_bundle(graph, f"paciente-{paciente.nombre}-{paciente.apellido}", schema)


def export_pacientes_rdf(request):
    pacientes = list(Paciente.objects.all())
    graph = _graph_with_resources(pacientes=pacientes)
    schema = build_fhir_schema(include_patients=True)
    return _export_bundle(graph, "pacientes-fhir", schema)


def export_procedimiento_rdf(request, procedimiento_id):
    procedimiento = Procedimiento.objects.select_related(
        "codigo",
        "paciente",
        "practicante",
        "diente",
    ).get(id=procedimiento_id)

    graph = _graph_with_resources(
        pacientes=[procedimiento.paciente],
        practicantes=[procedimiento.practicante],
        procedimientos=[procedimiento],
    )
    schema = build_fhir_schema(
        include_patients=True,
        include_practitioners=True,
        include_procedures=True,
    )
    return _export_bundle(graph, f"procedimiento-{procedimiento.id}", schema)


def export_procedimientos_rdf(request):
    procedimientos = list(
        Procedimiento.objects.select_related("codigo", "paciente", "practicante", "diente").all()
    )
    pacientes = list({proc.paciente_id: proc.paciente for proc in procedimientos}.values())
    practicantes = list({proc.practicante_id: proc.practicante for proc in procedimientos}.values())

    graph = _graph_with_resources(
        pacientes=pacientes,
        practicantes=practicantes,
        procedimientos=procedimientos,
    )
    schema = build_fhir_schema(
        include_patients=bool(pacientes),
        include_practitioners=bool(practicantes),
        include_procedures=True,
    )
    return _export_bundle(graph, "procedimientos-fhir", schema)


def export_practitioners_rdf(request):
    practicantes = list(Practicante.objects.all())
    graph = _graph_with_resources(practicantes=practicantes)
    schema = build_fhir_schema(include_practitioners=True)
    return _export_bundle(graph, "practicantes-fhir", schema)


def export_teeth_rdf(request):
    teeth_graph = _new_graph()
    for diente in Diente.objects.all():
        diente_uri = URIRef(FHIR.Tooth + "/" + str(diente.id))
        teeth_graph.add((diente_uri, RDF.type, FHIR.Tooth))
        _add_wrapped_literal(teeth_graph, diente_uri, FHIR["Tooth.code"], diente.codigo)
        _add_wrapped_literal(teeth_graph, diente_uri, FHIR["Tooth.display"], diente.display)
        _add_wrapped_literal(teeth_graph, diente_uri, FHIR["Tooth.definition"], diente.definicion)

    return teeth_graph.serialize(format="turtle")


def build_patient_rdf(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    include_patient = request.GET.get("exportar_paciente") == "on"
    procedimientos = list(
        Procedimiento.objects.select_related("codigo", "diente", "practicante").filter(paciente=paciente)
    )
    practicantes = list({proc.practicante_id: proc.practicante for proc in procedimientos}.values())
    include_patient = include_patient or not procedimientos

    graph = _graph_with_resources(
        pacientes=[paciente] if include_patient else [],
        practicantes=practicantes,
        procedimientos=procedimientos,
    )
    schema = build_fhir_schema(
        include_patients=include_patient,
        include_practitioners=bool(practicantes),
        include_procedures=bool(procedimientos),
    )
    return _export_bundle(graph, f"historial-{paciente.nombre}-{paciente.apellido}", schema)


def patient_rdf_graph(graph, paciente):
    paciente_uri = URIRef(FHIR.Patient + "/" + str(paciente.id))
    graph.add((paciente_uri, RDF.type, FHIR.Patient))

    _add_wrapped_literal(graph, paciente_uri, FHIR["Patient.active"], paciente.activo, datatype=XSD.boolean)

    name = BNode()
    graph.add((paciente_uri, FHIR["Patient.name"], name))
    _add_wrapped_literal(graph, name, FHIR["HumanName.family"], paciente.apellido)
    _add_wrapped_literal(graph, name, FHIR["HumanName.given"], paciente.nombre)

    telecom = BNode()
    graph.add((paciente_uri, FHIR["Patient.telecom"], telecom))
    graph.add((telecom, FHIR["index"], Literal(0)))
    _add_wrapped_literal(graph, telecom, FHIR["ContactPoint.system"], "phone")
    _add_wrapped_literal(graph, telecom, FHIR["ContactPoint.value"], paciente.telefono or "")

    _add_wrapped_literal(graph, paciente_uri, FHIR["Patient.gender"], paciente.genero)
    _add_wrapped_literal(
        graph,
        paciente_uri,
        FHIR["Patient.birthDate"],
        paciente.fecha_nacimiento,
        datatype=XSD.date,
    )
    _add_wrapped_literal(graph, paciente_uri, FHIR["Patient.maritalStatus"], paciente.estado_civil)

    address = BNode()
    graph.add((paciente_uri, FHIR["Patient.address"], address))
    _add_wrapped_literal(graph, address, FHIR["Address.line"], paciente.calle or "")
    _add_wrapped_literal(graph, address, FHIR["Address.city"], paciente.ciudad or "")
    _add_wrapped_literal(graph, address, FHIR["Address.state"], paciente.provincia or "")
    _add_wrapped_literal(graph, address, FHIR["Address.postalCode"], paciente.codigo_postal or "")
    _add_wrapped_literal(graph, address, FHIR["Address.country"], paciente.pais or "")

    return paciente_uri


def practitioner_rdf_graph(graph, practicante):
    practitioner_uri = URIRef(FHIR.Practitioner + "/" + str(practicante.id))
    graph.add((practitioner_uri, RDF.type, FHIR.Practitioner))

    _add_wrapped_literal(graph, practitioner_uri, FHIR["Practitioner.active"], practicante.activo, datatype=XSD.boolean)

    name = BNode()
    graph.add((practitioner_uri, FHIR["Practitioner.name"], name))
    _add_wrapped_literal(graph, name, FHIR["HumanName.family"], practicante.apellido)
    _add_wrapped_literal(graph, name, FHIR["HumanName.given"], practicante.nombre)

    telecom = BNode()
    graph.add((practitioner_uri, FHIR["Practitioner.telecom"], telecom))
    graph.add((telecom, FHIR["index"], Literal(0)))
    _add_wrapped_literal(graph, telecom, FHIR["ContactPoint.system"], "phone")
    _add_wrapped_literal(graph, telecom, FHIR["ContactPoint.value"], practicante.telefono or "")

    _add_wrapped_literal(
        graph,
        practitioner_uri,
        FHIR["Practitioner.gender"],
        PRACTITIONER_TO_FHIR_GENDER.get(practicante.genero, "unknown"),
    )

    qualification = BNode()
    graph.add((practitioner_uri, FHIR["Practitioner.qualification"], qualification))
    _add_wrapped_literal(
        graph,
        qualification,
        FHIR["CodeableConcept.text"],
        practicante.cualificacion or "Importado desde FHIR",
    )

    return practitioner_uri


def procedimiento_rdf_graph(graph, procedimiento):
    procedure_uri = URIRef(FHIR.Procedure + "/" + str(procedimiento.id))
    graph.add((procedure_uri, RDF.type, FHIR.Procedure))

    _add_wrapped_literal(graph, procedure_uri, FHIR["Procedure.status"], procedimiento.status)

    codeable_concept = BNode()
    graph.add((procedure_uri, FHIR["Procedure.code"], codeable_concept))

    coding = BNode()
    graph.add((codeable_concept, FHIR["CodeableConcept.coding"], coding))
    _add_wrapped_literal(graph, coding, FHIR["Coding.code"], procedimiento.codigo.codigo)
    _add_wrapped_literal(graph, coding, FHIR["Coding.system"], "http://ada.org/cdt", datatype=XSD.anyURI)
    _add_wrapped_literal(graph, codeable_concept, FHIR["CodeableConcept.text"], procedimiento.codigo.text)

    _add_wrapped_literal(
        graph,
        procedure_uri,
        FHIR["Procedure.performedDateTime"],
        procedimiento.realizado_el,
        datatype=XSD.date,
    )

    subject = BNode()
    graph.add((procedure_uri, FHIR["Procedure.subject"], subject))
    _add_wrapped_literal(graph, subject, FHIR["Reference.reference"], f"Patient/{procedimiento.paciente.id}")

    performer = BNode()
    actor = BNode()
    graph.add((procedure_uri, FHIR["Procedure.performer"], performer))
    graph.add((performer, FHIR["Procedure.performer.actor"], actor))
    _add_wrapped_literal(graph, actor, FHIR["Reference.reference"], f"Practitioner/{procedimiento.practicante.id}")

    if procedimiento.diente:
        body_site = BNode()
        coding_body_site = BNode()
        graph.add((procedure_uri, FHIR["Procedure.bodySite"], body_site))
        graph.add((body_site, FHIR["CodeableConcept.coding"], coding_body_site))
        _add_wrapped_literal(graph, coding_body_site, FHIR["Coding.code"], procedimiento.diente.codigo)
        _add_wrapped_literal(
            graph,
            coding_body_site,
            FHIR["Coding.system"],
            "http://ada.org/snodent",
            datatype=XSD.anyURI,
        )
        _add_wrapped_literal(graph, coding_body_site, FHIR["Coding.display"], procedimiento.diente.display)

        if procedimiento.diente.definicion:
            _add_wrapped_literal(graph, body_site, FHIR["CodeableConcept.text"], procedimiento.diente.definicion)

    return procedure_uri


def import_data(form):
    rdf_content = _read_uploaded_text(form.cleaned_data["rdf_file"], "RDF")
    shex_content = _read_uploaded_text(form.cleaned_data["shex_file"], "ShEx")

    graph = Graph()
    try:
        graph.parse(data=rdf_content, format="turtle")
    except Exception as exc:
        raise ValidationError(f"El archivo RDF no se pudo procesar como Turtle valido: {exc}") from exc

    shex_errors, _, focus_map = validate_uploaded_schema(graph, shex_content)
    if not focus_map:
        raise ValidationError("El RDF no contiene recursos FHIR Patient, Practitioner o Procedure compatibles con la importacion.")
    link_errors = _validate_resource_links(graph)
    all_errors = shex_errors + link_errors

    if all_errors:
        raise ValidationError(all_errors)

    return _persist_resources(graph, focus_map)


def _validate_resource_links(graph):
    errors = []
    focus_map = detect_focus_nodes(graph)

    imported_patient_ids = {
        _numeric_identifier(subject)
        for subject in focus_map.get(PATIENT_SHAPE, [])
        if _numeric_identifier(subject) is not None
    }

    for procedure_subject in focus_map.get(PROCEDURE_SHAPE, []):
        procedure_id = _resource_identifier(procedure_subject) or "desconocido"
        patient_reference = _reference_value(graph, procedure_subject, FHIR["Procedure.subject"])
        patient_id = _numeric_identifier(patient_reference)

        if patient_id is None:
            errors.append(
                f"El procedimiento {procedure_id} referencia un paciente no numerico o no compatible con la aplicacion."
            )
            continue

        if patient_id not in imported_patient_ids and not Paciente.objects.filter(id=patient_id).exists():
            errors.append(
                f"El procedimiento {procedure_id} referencia al paciente {patient_id}, que no esta en el RDF ni en la base de datos."
            )

    return errors


def _persist_resources(graph, focus_map):
    imported = {
        "pacientes": {"creados": 0, "actualizados": 0},
        "practicantes": {"creados": 0, "actualizados": 0},
        "procedimientos": {"creados": 0, "actualizados": 0},
    }
    practitioner_cache = {}

    with transaction.atomic():
        for patient_subject in focus_map.get(PATIENT_SHAPE, []):
            patient_id = _numeric_identifier(patient_subject)
            if patient_id is None:
                raise ValidationError(
                    f"El paciente {_resource_identifier(patient_subject) or patient_subject} no tiene un identificador numerico compatible."
                )

            defaults = {
                "activo": bool(_wrapped_value(graph, patient_subject, FHIR["Patient.active"], True)),
                "nombre": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.name"]),
                    FHIR["HumanName.given"],
                    "",
                ),
                "apellido": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.name"]),
                    FHIR["HumanName.family"],
                    "",
                ),
                "genero": Paciente.normalizar_genero(
                    _wrapped_value(graph, patient_subject, FHIR["Patient.gender"], "unknown")
                ),
                "telefono": _telecom_value(graph, patient_subject, FHIR["Patient.telecom"]),
                "fecha_nacimiento": _wrapped_value(graph, patient_subject, FHIR["Patient.birthDate"]),
                "calle": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.address"]),
                    FHIR["Address.line"],
                    "",
                ),
                "ciudad": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.address"]),
                    FHIR["Address.city"],
                    "",
                ),
                "provincia": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.address"]),
                    FHIR["Address.state"],
                    "",
                ),
                "codigo_postal": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.address"]),
                    FHIR["Address.postalCode"],
                    "",
                ),
                "pais": _wrapped_value(
                    graph,
                    graph.value(patient_subject, FHIR["Patient.address"]),
                    FHIR["Address.country"],
                    "",
                ),
                "estado_civil": Paciente.normalizar_estado_civil(
                    _wrapped_value(graph, patient_subject, FHIR["Patient.maritalStatus"], "UNK")
                ),
            }

            _, created = Paciente.objects.update_or_create(id=patient_id, defaults=defaults)
            imported["pacientes"]["creados" if created else "actualizados"] += 1

        for practitioner_subject in focus_map.get(PRACTITIONER_SHAPE, []):
            practitioner_reference = str(practitioner_subject)
            practitioner_id = _numeric_identifier(practitioner_subject)

            defaults = {
                "activo": bool(_wrapped_value(graph, practitioner_subject, FHIR["Practitioner.active"], True)),
                "nombre": _wrapped_value(
                    graph,
                    graph.value(practitioner_subject, FHIR["Practitioner.name"]),
                    FHIR["HumanName.given"],
                    "",
                ),
                "apellido": _wrapped_value(
                    graph,
                    graph.value(practitioner_subject, FHIR["Practitioner.name"]),
                    FHIR["HumanName.family"],
                    "",
                ),
                "genero": FHIR_TO_PRACTITIONER_GENDER.get(
                    _wrapped_value(graph, practitioner_subject, FHIR["Practitioner.gender"], "unknown"),
                    "O",
                ),
                "telefono": _telecom_value(graph, practitioner_subject, FHIR["Practitioner.telecom"]),
                "cualificacion": _wrapped_value(
                    graph,
                    graph.value(practitioner_subject, FHIR["Practitioner.qualification"]),
                    FHIR["CodeableConcept.text"],
                    "Importado desde FHIR",
                ),
            }

            practitioner, created = _upsert_practitioner(
                practitioner_id=practitioner_id,
                practitioner_reference=practitioner_reference,
                defaults=defaults,
            )
            practitioner_cache[practitioner_reference] = practitioner
            practitioner_cache[f"Practitioner/{practitioner.id}"] = practitioner
            imported["practicantes"]["creados" if created else "actualizados"] += 1

        for procedure_subject in focus_map.get(PROCEDURE_SHAPE, []):
            procedure_id = _numeric_identifier(procedure_subject)
            if procedure_id is None:
                raise ValidationError(
                    f"El procedimiento {_resource_identifier(procedure_subject) or procedure_subject} no tiene un identificador numerico compatible."
                )

            patient_reference = _reference_value(graph, procedure_subject, FHIR["Procedure.subject"])
            patient_id = _numeric_identifier(patient_reference)
            paciente = Paciente.objects.get(id=patient_id)

            practitioner_reference = _procedure_practitioner_reference(graph, procedure_subject)
            practicante = _resolve_practitioner_reference(practitioner_reference, practitioner_cache)

            procedure_code = _procedure_code(graph, procedure_subject) or "UNKNOWN"
            procedure_text = _procedure_text(graph, procedure_subject) or procedure_code

            catalogo, _ = ProcedimientoCatalogo.objects.get_or_create(
                codigo=procedure_code,
                defaults={"text": procedure_text},
            )
            if procedure_text and catalogo.text != procedure_text:
                catalogo.text = procedure_text
                catalogo.save(update_fields=["text"])

            tooth_code = _procedure_tooth_code(graph, procedure_subject)
            diente = Diente.objects.filter(codigo=tooth_code).first() if tooth_code else None

            defaults = {
                "status": _wrapped_value(graph, procedure_subject, FHIR["Procedure.status"], "unknown"),
                "codigo": catalogo,
                "paciente": paciente,
                "practicante": practicante,
                "practicante_externo_uri": _absolute_reference(practitioner_reference),
                "diente": diente,
                "descripcion": _procedure_description(graph, procedure_subject, fallback=procedure_text),
                "realizado_el": _wrapped_value(graph, procedure_subject, FHIR["Procedure.performedDateTime"]),
            }

            _, created = Procedimiento.objects.update_or_create(id=procedure_id, defaults=defaults)
            imported["procedimientos"]["creados" if created else "actualizados"] += 1

    return imported


def _upsert_practitioner(*, practitioner_id, practitioner_reference, defaults):
    if practitioner_id is not None:
        return Practicante.objects.update_or_create(id=practitioner_id, defaults=defaults)

    existing = Practicante.objects.filter(
        nombre=defaults["nombre"],
        apellido=defaults["apellido"],
        telefono=defaults["telefono"],
    ).first()

    if existing:
        for field_name, field_value in defaults.items():
            setattr(existing, field_name, field_value)
        existing.save()
        return existing, False

    created = Practicante.objects.create(**defaults)
    return created, True


def _resolve_practitioner_reference(reference_value, practitioner_cache):
    if not reference_value:
        raise ValidationError("El procedimiento importado no contiene referencia a un practicante.")

    if reference_value in practitioner_cache:
        return practitioner_cache[reference_value]

    practitioner_id = _numeric_identifier(reference_value)
    if practitioner_id is not None:
        practitioner = Practicante.objects.filter(id=practitioner_id).first()
        if practitioner:
            practitioner_cache[reference_value] = practitioner
            return practitioner

        practitioner = Practicante.objects.create(
            id=practitioner_id,
            activo=True,
            nombre="Profesional",
            apellido=f"FHIR {practitioner_id}",
            genero="O",
            telefono="",
            cualificacion="Importado desde referencia FHIR",
        )
        practitioner_cache[reference_value] = practitioner
        practitioner_cache[f"Practitioner/{practitioner_id}"] = practitioner
        return practitioner

    practitioner = Practicante.objects.create(
        activo=True,
        nombre="Profesional",
        apellido="FHIR externo",
        genero="O",
        telefono="",
        cualificacion="Importado desde referencia FHIR",
    )
    practitioner_cache[reference_value] = practitioner
    return practitioner


def _procedure_practitioner_reference(graph, procedure_subject):
    performer = graph.value(procedure_subject, FHIR["Procedure.performer"])
    if performer is None:
        return None
    actor = graph.value(performer, FHIR["Procedure.performer.actor"])
    if actor is None:
        return None
    return _wrapped_value(graph, actor, FHIR["Reference.reference"])


def _procedure_code(graph, procedure_subject):
    codeable_concept = graph.value(procedure_subject, FHIR["Procedure.code"])
    if codeable_concept is None:
        return None
    coding = graph.value(codeable_concept, FHIR["CodeableConcept.coding"])
    if coding is None:
        return None
    return _wrapped_value(graph, coding, FHIR["Coding.code"])


def _procedure_text(graph, procedure_subject):
    codeable_concept = graph.value(procedure_subject, FHIR["Procedure.code"])
    if codeable_concept is None:
        return None
    return _wrapped_value(graph, codeable_concept, FHIR["CodeableConcept.text"])


def _procedure_tooth_code(graph, procedure_subject):
    body_site = graph.value(procedure_subject, FHIR["Procedure.bodySite"])
    if body_site is None:
        return None
    coding = graph.value(body_site, FHIR["CodeableConcept.coding"])
    if coding is None:
        return None
    return _wrapped_value(graph, coding, FHIR["Coding.code"])


def _procedure_description(graph, procedure_subject, fallback=""):
    body_site = graph.value(procedure_subject, FHIR["Procedure.bodySite"])
    if body_site is not None:
        description = _wrapped_value(graph, body_site, FHIR["CodeableConcept.text"])
        if description:
            return description

        coding = graph.value(body_site, FHIR["CodeableConcept.coding"])
        display = _wrapped_value(graph, coding, FHIR["Coding.display"]) if coding else None
        if display:
            return display

    return fallback or ""
