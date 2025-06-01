from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, FOAF, XSD
from django.http import HttpResponse
from django.conf import settings
from .models import Procedimiento, Paciente, Practicante, Diente

import os
import tempfile
import shutil
import zipfile
from django.http import FileResponse

def export_all_rdf(request):
   
    temp_dir = tempfile.mkdtemp()

    try:
        export_pacientes_rdf(temp_dir)
        """ export_practitioners_rdf(temp_dir)
        export_teeth_rdf(temp_dir) """
        export_procedimientos_rdf(temp_dir)

        zip_path = os.path.join(temp_dir, "rdf_exports.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in os.listdir(temp_dir):
                if filename.endswith(".ttl"):
                    file_path = os.path.join(temp_dir, filename)
                    zipf.write(file_path, arcname=filename)

        return FileResponse(open(zip_path, 'rb'), as_attachment=True, filename="rdf_exports.zip")

    finally:
        shutil.rmtree(temp_dir)

def export_pacientes_rdf(request):
    g = Graph()

    FHIR = Namespace("http://hl7.org/fhir/")

    g.bind("fhir", FHIR)

    pacientes = Paciente.objects.all()

    for paciente in pacientes:
        #print("ID:",str(paciente.id))
        pac_uri = URIRef(FHIR.identifier + "/" + str(paciente.id))
        print(pac_uri)
        
        g.add((pac_uri, RDF.type, FHIR.Patient))

        g.add((pac_uri, FHIR.active, Literal(paciente.activo)))

        name = BNode()
        g.add((pac_uri, FHIR.name, name))
        g.add((name, FHIR.given, Literal(paciente.nombre)))
        g.add((name, FHIR.family, Literal(paciente.apellido)))

        telcom = BNode()
        telephone = BNode()
        email = BNode()
        g.add((pac_uri, FHIR.telecom, telcom))
        g.add((telephone, FHIR.system, Literal("phone")))
        g.add((telephone, FHIR.value, Literal(paciente.telefono)))
        g.add((telcom, FHIR.ContactPoint, telephone))

        '''
        g.add((email, FHIR.system, Literal("email")))
        g.add((email, FHIR.value, Literal(paciente.email)))
        g.add((telcom, FHIR.ContactPoint, email))  
        '''
        
        g.add((pac_uri, FHIR.gender, Literal(paciente.genero)))
        g.add((pac_uri, FHIR.birthDate, Literal(paciente.fecha_nacimiento, datatype=XSD.date)))

    rdf_data = g.serialize(format="turtle")

    """ response = HttpResponse(rdf_data, content_type="text/turtle")
    response["Content-Disposition"] = 'attachment; filename="pacients.ttl"'  """

    return rdf_data

def export_procedimientos_rdf(request):
    tmp_dir = tempfile.mkdtemp()
    rdf_file = os.path.join(tmp_dir, "procedures.ttl")
    shex_file = os.path.join(tmp_dir, "procedure-schemas.shex")
    zip_path = os.path.join(tmp_dir, "export.zip")

    g = Graph()

    FHIR = Namespace("http://hl7.org/fhir/")

    g.bind("fhir", FHIR)

    procedimientos = Procedimiento.objects.all()

    for procedimiento in procedimientos:
        #print("ID:",str(procedimiento.id))
        proc_uri = URIRef(FHIR.identifier + "/" + str(procedimiento.id))

        g.add((proc_uri, RDF.type, FHIR.Procedure))

        g.add((proc_uri, FHIR.Procedure.status, Literal(procedimiento.status)))

        procCode = BNode()
        code = BNode()
        g.add((code, FHIR.system, Literal("http://ada.org/cdt")))
        g.add((code, FHIR.code, Literal(procedimiento.codigo)))
        g.add((code, FHIR.display, Literal(procedimiento.descripcion)))
        g.add((procCode, FHIR.coding, code))
        g.add((proc_uri, FHIR.code, procCode))

        pacient_reference = BNode()
        g.add((pacient_reference, FHIR.value, Literal(f"Patient/{procedimiento.paciente.id}")))
        g.add((proc_uri, FHIR.subject, pacient_reference))

        g.add((proc_uri, FHIR.performedDateTime, Literal(procedimiento.realizado_el, datatype=XSD.date)))

        actor = BNode()
        actor_reference = BNode()
        performer = BNode()
        g.add((actor_reference, FHIR.value, Literal(f"Practitioner/{procedimiento.practicante.id}")))
        g.add((actor, FHIR.reference, actor_reference))
        g.add((performer, FHIR.actor, actor))
        g.add((proc_uri, FHIR.performer, performer))

        #g.add((proc_uri, FHIR.bodySite, Literal(procedimiento.diente)))
        
    rdf_data = g.serialize(format="turtle")

    """ shex_path = os.path.join(settings.BASE_DIR, "clinicaDental", "schemas", "procedure-schemas.shex")
    shutil.copy(shex_path, shex_file)

     # 3. Create zip
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(rdf_file, "procedures.ttl")
        zipf.write(shex_file, "procedure-schema.shex")

    # 4. Serve the zip
    with open(zip_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="fhir_procedure_export.zip"'
        return response

    response = HttpResponse(rdf_data, content_type="text/turtle")
    response["Content-Disposition"] = 'attachment; filename="procedures.ttl"'  """

    return rdf_data

def export_practitioners_rdf(request):
    g = Graph()

    FHIR = Namespace("http://hl7.org/fhir/")

    g.bind("fhir", FHIR)

    practitioners = Practicante.objects.all()

    for practitioner in practitioners:
        #print("ID:",str(practitioner.id))
        pract_uri = URIRef(FHIR.identifier + "/" + str(practitioner.id))
        print(pract_uri)
        
        g.add((pract_uri, RDF.type, FHIR.Practitioner))

        g.add((pract_uri, FHIR.active, Literal(practitioner.activo)))

        name = BNode()
        g.add((pract_uri, FHIR.name, name))
        g.add((name, FHIR.given, Literal(practitioner.nombre)))
        g.add((name, FHIR.family, Literal(practitioner.apellido)))

        telcom = BNode()
        telephone = BNode()
        g.add((pract_uri, FHIR.telecom, telcom))
        g.add((telephone, FHIR.system, Literal("phone")))
        g.add((telephone, FHIR.value, Literal(practitioner.telefono)))
        g.add((telcom, FHIR.ContactPoint, telephone))
        
    rdf_data = g.serialize(format="turtle")

    response = HttpResponse(rdf_data, content_type="text/turtle")
    response["Content-Disposition"] = 'attachment; filename="practicantes.ttl"' 

    return response

def export_teeth_rdf(request):
    g = Graph()

    FHIR = Namespace("http://hl7.org/fhir/")

    g.bind("fhir", FHIR)

    dientes = Diente.objects.all()

    for diente in dientes:
        #print("ID:",str(diente.id))
        diente_uri = URIRef(FHIR.identifier + "/" + str(diente.id))
        print(diente_uri)
        
        g.add((diente_uri, RDF.type, FHIR.Tooth))

        g.add((diente_uri, FHIR.active, Literal(diente.activo)))

        name = BNode()
        g.add((diente_uri, FHIR.name, name))
        g.add((name, FHIR.given, Literal(diente.nombre)))
        g.add((name, FHIR.family, Literal(diente.apellido)))

        telcom = BNode()
        telephone = BNode()
        g.add((diente_uri, FHIR.telecom, telcom))
        g.add((telephone, FHIR.system, Literal("phone")))
        g.add((telephone, FHIR.value, Literal(diente.telefono)))
        g.add((telcom, FHIR.ContactPoint, telephone))
        
    rdf_data = g.serialize(format="turtle")

    """ response = HttpResponse(rdf_data, content_type="text/turtle")
    response["Content-Disposition"] = 'attachment; filename="dientes.ttl"'  """

    return rdf_data

def build_patient_rdf(patient_id):
    from rdflib import Graph, URIRef, Literal, Namespace, BNode
    from rdflib.namespace import RDF, XSD

    FHIR = Namespace("http://hl7.org/fhir/")
    EX = Namespace("http://example.org/")

    g = Graph()
    g.bind("fhir", FHIR)
    g.bind("ex", EX)

    paciente = Paciente.objects.get(id=patient_id)
    procedimientos = Procedimiento.objects.select_related("diente", "practicante").filter(paciente=paciente)

    for procedimiento in procedimientos:
        #print("ID:",str(procedimiento.id))
        proc_uri = URIRef(FHIR.identifier + "/" + str(procedimiento.id))

        g.add((proc_uri, RDF.type, FHIR.Procedure))

        g.add((proc_uri, FHIR.status, Literal(procedimiento.status)))

        procCode = BNode()
        code = BNode()
        g.add((code, FHIR.system, Literal("http://ada.org/cdt")))
        g.add((code, FHIR.code, Literal(procedimiento.codigo)))
        g.add((procCode, FHIR.text, Literal(procedimiento.descripcion)))
        g.add((procCode, FHIR.coding, code))
        g.add((proc_uri, FHIR.code, procCode))

        pacient_reference = BNode()
        g.add((pacient_reference, FHIR.value, Literal(f"Patient/{procedimiento.paciente.id}")))
        g.add((proc_uri, FHIR.subject, pacient_reference))

        g.add((proc_uri, FHIR.performedDateTime, Literal(procedimiento.realizado_el, datatype=XSD.date)))

        actor = BNode()
        actor_reference = BNode()
        performer = BNode()
        g.add((actor_reference, FHIR.value, Literal(f"Practitioner/{procedimiento.practicante.id}")))
        g.add((actor, FHIR.reference, actor_reference))
        g.add((performer, FHIR.actor, actor))
        g.add((proc_uri, FHIR.performer, performer))
        if procedimiento.diente:
            location = BNode()
            coding = BNode()
            system_code = BNode()
            code_code = BNode()
            display_code = BNode()

            g.add((system_code, FHIR.system, Literal("http://ada.org/tooth")))
            g.add((code_code, FHIR.code, Literal(procedimiento.diente.codigo)))
            g.add((display_code, FHIR.display, Literal(procedimiento.diente.display)))
            
            g.add((coding, FHIR.system, system_code))
            g.add((coding, FHIR.code, code_code))
            g.add((coding, FHIR.display, display_code))

            g.add((location, FHIR.coding, coding))
            g.add((proc_uri, FHIR.location, location))
            

    return g

def export_patient_rdf(request, paciente_id):
    g = build_patient_rdf(paciente_id)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ttl")
    g.serialize(destination=tmp.name, format="turtle")

    return FileResponse(open(tmp.name, "rb"), as_attachment=True, filename=f"paciente_{paciente_id}_procedures.ttl")
