from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, FOAF
from django.http import HttpResponse
from .models import Procedimiento


def export_procedimientos_rdf(request):
    g = Graph()

    FHIR = Namespace("http://hl7.org/fhir/")

    g.bind("fhir", FHIR)

    procedimientos = Procedimiento.objects.all()

    for procedimiento in procedimientos:
        # Define a unique subject URI for each procedimiento
        #print("ID:",str(procedimiento.id))
        proc_uri = URIRef(FHIR.identifier + "/" + str(procedimiento.id))
        print(proc_uri)
        # Add triples
        g.add((proc_uri, RDF.type, FHIR.Procedure))
        g.add((proc_uri, FHIR.code, Literal(procedimiento.codigo)))
        g.add((proc_uri, FHIR.status, Literal(procedimiento.status)))
        g.add((proc_uri, FHIR.description, Literal(procedimiento.descripcion)))
        g.add(
            (
                proc_uri,
                FHIR.recorded,
                Literal(procedimiento.realizado_el.isoformat()),
            )
        )
        g.add((proc_uri, FHIR.diente, Literal(procedimiento.diente)))

        # Link to Paciente
        paciente_uri = URIRef(
            f"http://example.org/paciente/{procedimiento.paciente.id}"
        )
        g.add((proc_uri, FHIR.subject, paciente_uri))

    # Serialize the graph
    rdf_data = g.serialize(format="turtle")

    # Return it as a file download
    response = HttpResponse(rdf_data, content_type="text/turtle")
    response["Content-Disposition"] = 'attachment; filename="procedimientos.ttl"' 

    return response
