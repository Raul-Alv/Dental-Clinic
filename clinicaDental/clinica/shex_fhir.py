from collections import OrderedDict

from pyshex import ShExEvaluator
from rdflib import Namespace, URIRef
from rdflib.namespace import RDF


FHIR = Namespace("http://hl7.org/fhir/")

PATIENT_SHAPE = "PatientShape"
PRACTITIONER_SHAPE = "PractitionerShape"
PROCEDURE_SHAPE = "ProcedureShape"


_PREFIXES = """PREFIX fhir: <http://hl7.org/fhir/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""

_PATIENT_SHAPE_DEF = """<PatientShape> {
  rdf:type [ fhir:Patient ] ;
  fhir:Patient.active @<ValueBooleanShape> ;
  fhir:Patient.name @<HumanNameShape>+ ;
  fhir:Patient.gender @<GenderShape> ;
  fhir:Patient.birthDate @<ValueDateShape> ;
  fhir:Patient.maritalStatus @<MaritalStatusShape> ;
  fhir:Patient.telecom @<TelecomShape>* ;
  fhir:Patient.address @<AddressShape>* ;
}"""

_PRACTITIONER_SHAPE_DEF = """<PractitionerShape> {
  rdf:type [ fhir:Practitioner ] ;
  fhir:Practitioner.active @<ValueBooleanShape> ;
  fhir:Practitioner.name @<HumanNameShape>+ ;
  fhir:Practitioner.gender @<GenderShape> ;
  fhir:Practitioner.telecom @<TelecomShape>* ;
  fhir:Practitioner.qualification @<QualificationShape>* ;
}"""

_PROCEDURE_SHAPE_DEF = """<ProcedureShape> {
  rdf:type [ fhir:Procedure ] ;
  fhir:Procedure.status @<ProcedureStatusShape> ;
  fhir:Procedure.code @<ProcedureCodeShape> ;
  fhir:Procedure.performedDateTime @<ValueDateShape> ;
  fhir:Procedure.subject @<ReferenceWrapperShape> ;
  fhir:Procedure.performer @<PerformerShape> ;
  fhir:Procedure.bodySite @<ProcedureBodySiteShape>* ;
}"""

_SHARED_SHAPES = """<HumanNameShape> {
  fhir:HumanName.family @<ValueStringShape> ;
  fhir:HumanName.given @<ValueStringShape>+ ;
}

<TelecomShape> {
  fhir:index xsd:integer ;
  fhir:ContactPoint.system @<ContactSystemShape> ;
  fhir:ContactPoint.value @<ValueStringShape> ;
}

<AddressShape> {
  fhir:Address.line @<ValueStringShape>+ ;
  fhir:Address.city @<ValueStringShape> ;
  fhir:Address.state @<ValueStringShape> ;
  fhir:Address.postalCode @<ValueStringShape> ;
  fhir:Address.country @<ValueStringShape> ;
}

<QualificationShape> {
  fhir:CodeableConcept.text @<ValueStringShape> ;
}

<ProcedureCodeShape> {
  fhir:CodeableConcept.coding @<ProcedureCodingShape>+ ;
  fhir:CodeableConcept.text @<ValueStringShape> ;
}

<ProcedureBodySiteShape> {
  fhir:CodeableConcept.coding @<BodySiteCodingShape>+ ;
  fhir:CodeableConcept.text @<ValueStringShape>* ;
}

<ProcedureCodingShape> {
  fhir:Coding.code @<ValueStringShape> ;
  fhir:Coding.system @<ValueURIShape> ;
  fhir:Coding.display @<ValueStringShape>* ;
}

<BodySiteCodingShape> {
  fhir:Coding.code @<ValueStringShape> ;
  fhir:Coding.system @<ValueURIShape> ;
  fhir:Coding.display @<ValueStringShape>* ;
}

<PerformerShape> {
  fhir:Procedure.performer.actor @<ReferenceWrapperShape> ;
}

<ReferenceWrapperShape> {
  fhir:Reference.reference @<ReferenceShape> ;
}

<ReferenceShape> {
  fhir:value xsd:string ;
}

<ValueBooleanShape> {
  fhir:value xsd:boolean ;
}

<ValueStringShape> {
  fhir:value xsd:string ;
}

<ValueDateShape> {
  fhir:value xsd:date ;
}

<ValueURIShape> {
  fhir:value xsd:anyURI ;
}

<GenderShape> {
  fhir:value [ "male" "female" "other" "unknown" ] ;
}

<MaritalStatusShape> {
  fhir:value [ "A" "D" "M" "U" "W" "UNK" ] ;
}

<ProcedureStatusShape> {
  fhir:value [ "preparation" "in-progress" "not-done" "on-hold" "stopped" "completed" "entered-in-error" "unknown" ] ;
}

<ContactSystemShape> {
  fhir:value [ "phone" "email" "url" "fax" "pager" "other" ] ;
}"""

_RESOURCE_TYPES = OrderedDict(
    (
        (PATIENT_SHAPE, URIRef(FHIR + "Patient")),
        (PRACTITIONER_SHAPE, URIRef(FHIR + "Practitioner")),
        (PROCEDURE_SHAPE, URIRef(FHIR + "Procedure")),
    )
)


def detect_focus_nodes(graph):
    focus_map = OrderedDict()

    for shape_name, resource_type in _RESOURCE_TYPES.items():
        subjects = list(dict.fromkeys(graph.subjects(RDF.type, resource_type)))
        if subjects:
            focus_map[shape_name] = subjects

    return focus_map


def build_fhir_schema(
    *,
    include_patients=False,
    include_practitioners=False,
    include_procedures=False,
    start_shape=None,
):
    included_shapes = []

    if include_patients:
        included_shapes.append(PATIENT_SHAPE)
    if include_practitioners:
        included_shapes.append(PRACTITIONER_SHAPE)
    if include_procedures:
        included_shapes.append(PROCEDURE_SHAPE)

    if not included_shapes:
        raise ValueError("No hay recursos FHIR compatibles para generar un esquema ShEx.")

    chosen_start = start_shape or included_shapes[0]
    sections = [_PREFIXES, f"start = @{_shape_ref(chosen_start)}"]

    if include_patients:
        sections.append(_PATIENT_SHAPE_DEF)
    if include_practitioners:
        sections.append(_PRACTITIONER_SHAPE_DEF)
    if include_procedures:
        sections.append(_PROCEDURE_SHAPE_DEF)

    sections.append(_SHARED_SHAPES)
    return "\n\n".join(sections).strip() + "\n"


def expected_schema_for_graph(graph):
    focus_map = detect_focus_nodes(graph)
    return build_fhir_schema(
        include_patients=PATIENT_SHAPE in focus_map,
        include_practitioners=PRACTITIONER_SHAPE in focus_map,
        include_procedures=PROCEDURE_SHAPE in focus_map,
        start_shape=next(iter(focus_map), None),
    )


def validate_graph(graph, schema_text, focus_map=None):
    focus_map = focus_map or detect_focus_nodes(graph)
    errors = []

    for shape_name, focus_nodes in focus_map.items():
        try:
            results = ShExEvaluator(
                rdf=graph,
                schema=schema_text,
                focus=focus_nodes,
                start=shape_name,
            ).evaluate()
        except Exception as exc:
            errors.append(f"El esquema ShEx no pudo evaluar {shape_name}: {exc}")
            continue

        for result in results:
            if not result.result:
                errors.append(
                    "El nodo "
                    f"{result.focus or 'desconocido'} no cumple {shape_name}: {result.reason or 'sin detalle.'}"
                )

    return errors


def validate_uploaded_schema(graph, uploaded_schema_text):
    focus_map = detect_focus_nodes(graph)

    if not focus_map:
        return [], "", focus_map

    errors = []
    if "http://hl7.org/fhir/" not in uploaded_schema_text:
        errors.append("El archivo ShEx subido no declara el namespace HL7 FHIR esperado.")

    for shape_name in focus_map:
        if _shape_ref(shape_name) not in uploaded_schema_text:
            errors.append(f"El archivo ShEx subido no contiene la forma requerida {_shape_ref(shape_name)}.")

    expected_schema = expected_schema_for_graph(graph)
    errors.extend(validate_graph(graph, uploaded_schema_text, focus_map=focus_map))
    errors.extend(validate_graph(graph, expected_schema, focus_map=focus_map))
    return errors, expected_schema, focus_map


def _shape_ref(shape_name):
    return f"<{shape_name}>"
