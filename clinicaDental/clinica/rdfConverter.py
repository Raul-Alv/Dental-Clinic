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

FHIR = Namespace("http://hl7.org/fhir/")

############################################################
#                                                          #
# ~~~~~~~~~~~~ Exportación de datos desde RDF ~~~~~~~~~~~~ #
#                                                          #
############################################################
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


####################################################
## Exportación de datos de un paciente específico ##
####################################################
def export_patient_rdf(request, paciente_id):
    g = Graph()
    paciente = Paciente.objects.get(id=paciente_id)
    g.bind("fhir", FHIR)

    patient_rdf_graph(g, paciente)

    return export_file(g, "paciente_" + paciente.nombre + ".ttl")

#####################################
## Exportación todos los pacientes ##
#####################################
def export_pacientes_rdf(request):
    g = Graph()

    g.bind("fhir", FHIR)

    pacientes = Paciente.objects.all()

    for paciente in pacientes:
        patient_rdf_graph(g, paciente)

    return export_file(g, "pacient' + paciente.nombre + '.ttl")

#########################################################
## Exportación de datos de un procedimiento específico ##
#########################################################
def export_procedimiento_rdf(request, procedimiento_id):
    g = Graph()
    procedimiento = Procedimiento.objects.get(id=procedimiento_id)
    g.bind("fhir", FHIR)

    procedimiento_rdf_graph(g, procedimiento)

    return export_file(g, "procedimiento_" + procedimiento.codigo + ".ttl")
    
##########################################
## Exportación todos los procedimientos ##
##########################################
def export_procedimientos_rdf(request):
    g = Graph()

    g.bind("fhir", FHIR)

    procedimientos = Procedimiento.objects.all()

    for procedimiento in procedimientos:
        procedimiento_rdf_graph(g, procedimiento)
        #print("ID:",str(procedimiento.id))

        #g.add((proc_uri, FHIR.bodySite, Literal(procedimiento.diente)))
        
    return export_file(g, "procedimientos_all.ttl")

def export_practitioners_rdf(request):
    g = Graph()

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

############################################################
#                                                          #
# ~~~~~~~~~~~~~~~~~ Funciones auxiliares ~~~~~~~~~~~~~~~~~ #
#                                                          #
############################################################

####################################################################################################
## Exportación de datos de un paciente específico con sus procedimientos asociados en formato RDF ##
####################################################################################################
def build_patient_rdf(request, paciente_id):
    EX = Namespace("http://example.org/")
    
    g = Graph()
    g.bind("fhir", FHIR)
    g.bind("ex", EX)
    
    paciente = Paciente.objects.get(id=paciente_id)
    exportar_paciente = request.GET.get("exportar_paciente") == "on"

    procedimientos = Procedimiento.objects.select_related("diente", "practicante").filter(paciente=paciente)

    if exportar_paciente:
        patient_rdf_graph(g, paciente)

    for procedimiento in procedimientos:
        procedimiento_rdf_graph(g, procedimiento)

    return export_file(g, "pacient-" + paciente.nombre + "-procedures.ttl")

########################################################################################
## Función para crear el grafo RDF de un paciente específico con sus datos personales ##
########################################################################################
def patient_rdf_graph(g, paciente):
    pac_uri = URIRef(FHIR.Patient + "/" + str(paciente.id))
    g.add((pac_uri, RDF.type, FHIR.Patient))

    g.add((pac_uri, FHIR.active, Literal(paciente.activo)))

    name = BNode()
    g.add((pac_uri, FHIR.name, name))
    g.add((name, FHIR.given, Literal(paciente.nombre)))
    g.add((name, FHIR.family, Literal(paciente.apellido)))

    telcom = BNode()
    telephone = BNode()

    g.add((pac_uri, FHIR.telecom, telcom))
    g.add((telephone, FHIR.system, Literal("phone")))
    g.add((telephone, FHIR.value, Literal(paciente.telefono)))
    g.add((telcom, FHIR.ContactPoint, telephone))
    
    g.add((pac_uri, FHIR.gender, Literal(paciente.genero)))
    g.add((pac_uri, FHIR.birthDate, Literal(paciente.fecha_nacimiento, datatype=XSD.date)))

    adress = BNode()
    g.add((pac_uri, FHIR.address, adress))
    g.add((adress, FHIR.line, Literal(paciente.calle)))
    g.add((adress, FHIR.city, Literal(paciente.ciudad)))
    g.add((adress, FHIR.state, Literal(paciente.provincia)))
    g.add((adress, FHIR.postalCode, Literal(paciente.codigo_postal)))
    g.add((adress, FHIR.country, Literal(paciente.pais)))

    g.add((pac_uri, FHIR.maritalStatus, Literal(paciente.estado_civil)))

####################################################################
## Función para crear el grafo RDF de un procedimiento específico ##
####################################################################
def procedimiento_rdf_graph(g, procedimiento):
    proc_uri = URIRef(FHIR.Procedure + "/" + str(procedimiento.id))

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
        bodySite = BNode()
        coding = BNode()

        g.add((coding, FHIR.system, Literal("http://ada.org/snodent")))
        g.add((coding, FHIR.code, Literal(procedimiento.diente.codigo)))
        g.add((coding, FHIR.display, Literal(procedimiento.diente.display)))

        g.add((bodySite, FHIR.coding, coding))
        g.add((bodySite, FHIR.text, Literal(procedimiento.diente.definicion)))

        g.add((proc_uri, FHIR.bodySite, bodySite))

####################################
## Función para exportar un grafo ##
####################################
def export_file(g, filename):
    rdf_data = g.serialize(format="turtle")
    response = HttpResponse(rdf_data, content_type="text/turtle")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

############################################################
#                                                          #
# ~~~~~~~~~~~~ Importación de datos desde RDF ~~~~~~~~~~~~ #
#                                                          #
############################################################
def import_data(request, form):
    rdf_file = form.cleaned_data['rdf_file']

    g = Graph()
    g.parse(rdf_file, format='turtle')  # or guess format

    # 1. Import Pacientes
    for s in g.subjects(RDF.type, URIRef(FHIR + "Patient")):
        patient_id = str(s).split("/")[-1]
        name = g.value(s, URIRef(FHIR + "name"))
        phone = ""
        for telecom_node in g.objects(s, FHIR.telecom):
            system = g.value(telecom_node, FHIR.system)
            if system and str(system) == "phone":
                phone = g.value(telecom_node, FHIR.value, default="")
                break
        if not Paciente.objects.filter(id=patient_id).exists():
            print(f"Importing Patient: {s}, ID: {patient_id}, Name: {name}")
            Paciente.objects.create(
                id=patient_id,
                activo=g.value(s, URIRef(FHIR + "active").toPython(), default=True),
                nombre=g.value(name, URIRef(FHIR + "given"), default=""),
                apellido=g.value(name, URIRef(FHIR + "family"), default=""),
                genero=g.value(s, URIRef(FHIR + "gender"), default="O").toPython(),
                telefono=phone,
                fecha_nacimiento=g.value(s, URIRef(FHIR + "birthDate"), default=None).toPython() if g.value(s, URIRef(FHIR + "birthDate")) else None,
                calle=g.value(g.value(s, URIRef(FHIR + "address")), URIRef(FHIR + "line"), default=""),
                ciudad=g.value(g.value(s, URIRef(FHIR + "address")), URIRef(FHIR + "city"), default=""),
                provincia=g.value(g.value(s, URIRef(FHIR + "address")), URIRef(FHIR + "state"), default=""),
                codigo_postal=g.value(g.value(s, URIRef(FHIR + "address")), URIRef(FHIR + "postalCode"), default=""),
                pais=g.value(g.value(s, URIRef(FHIR + "address")), URIRef(FHIR + "country"), default=""),
                estado_civil=g.value(s, URIRef(FHIR + "maritalStatus"), default="S").toPython() if g.value(s, URIRef(FHIR + "maritalStatus")) else "S",

            )

    # 2. Import Procedimientos
    for s in g.subjects(RDF.type, URIRef(FHIR + "Procedure")):
        status = g.value(s, URIRef(FHIR + "status"))

        body_site = g.value(s, URIRef(FHIR + "bodySite"))
        coding_node = g.value(body_site, FHIR.coding)

        code = g.value(coding_node, FHIR.code, default="")
        display = g.value(coding_node, FHIR.display, default="")
        descripcion = g.value(body_site, FHIR.text, default="")
        
        #print(f"Processing Procedure: {s}, Status: {status}, Code: {code}")
        date = g.value(s, URIRef(FHIR + "performedDateTime"))

        # Get patient
        patient_val = g.value(g.value(s, URIRef(FHIR + "subject")), URIRef(FHIR + "value"))
        paciente = None
        if patient_val:
            patient_id = str(patient_val).split("/")[-1]
            paciente = Paciente.objects.filter(id=patient_id).first()

        # ✅ Get practitioner
        practicante = None
        practitioner_uri = None

        practicante = g.value(s, URIRef(FHIR + "performer"))
        actor = g.value(practicante, URIRef(FHIR + "actor")) if practicante else None
        reference = g.value(actor, URIRef(FHIR + "reference")) if actor else None
        value = g.value(reference, URIRef(FHIR + "value")) if reference else None
        #print(f"Practitioner URI: {value}")
        if value:
            practitioner_id = str(value).split("/")[-1]
            practicante = Practicante.objects.filter(id=practitioner_id).first()
            if not practicante:
                practitioner_uri = str(value)  # Save raw reference for later/debug

        # ✅ Get tooth from bodySite
        diente = None
        body_site = g.value(s, URIRef(FHIR + "bodySite"))
        coding = g.value(body_site, URIRef(FHIR + "coding")) if body_site else None
        tooth_code = g.value(coding, URIRef(FHIR + "code")) if coding else None

        if tooth_code:
            diente = Diente.objects.filter(codigo=str(tooth_code)).first()

        #print(f"Importing Procedure: {s}, Status: {status}, Code: {code}, Date: {date}, Patient: {paciente}, Practitioner: {practicante}, Pract_uri: {practitioner_uri} Tooth: {diente}")


        # ✅ Create the procedure
        Procedimiento.objects.create(
            id=str(s).split("/")[-1],  # Use the URI as the ID
            codigo=code if code else "UNKNOWN",
            status=status.toPython() if status else "unknown",
            paciente=paciente,
            practicante=practicante,
            practicante_externo_uri=practitioner_uri,  # Save the raw URI if needed
            diente=diente,
            descripcion=descripcion if descripcion else display, 
            realizado_el=date.toPython() if date else None,
            # optional: you could save `practitioner_uri` or `tooth_code` as raw text fields for traceability
        ) 


    