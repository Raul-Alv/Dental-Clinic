import io
import zipfile
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rdflib import Graph
from rdflib.namespace import RDF

from .models import Diente, Paciente, Practicante, Procedimiento, ProcedimientoCatalogo
from .shex_fhir import FHIR


class ShexImportExportTests(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            calle="Calle Mayor 1",
            ciudad="Oviedo",
            provincia="Asturias",
            codigo_postal="33001",
            pais="Espana",
            estado_civil="U",
        )
        self.practicante = Practicante.objects.create(
            nombre="Marta",
            apellido="Sanz",
            genero="F",
            telefono="123123123",
            cualificacion="Odontologa",
        )
        self.catalogo = ProcedimientoCatalogo.objects.create(
            codigo="ABC123",
            text="Limpieza dental",
        )
        self.diente = Diente.objects.create(
            codigo="T-11",
            display="Incisivo central superior derecho",
            definicion="Incisivo central superior derecho",
        )
        self.procedimiento = Procedimiento.objects.create(
            codigo=self.catalogo,
            paciente=self.paciente,
            practicante=self.practicante,
            diente=self.diente,
            descripcion="Revision y limpieza",
            realizado_el=date(2026, 5, 10),
            status="completed",
        )

    def test_import_view_requires_rdf_and_shex_files(self):
        response = self.client.post(
            reverse("import_data"),
            {
                "rdf_file": SimpleUploadedFile("paciente.ttl", b"@prefix fhir: <http://hl7.org/fhir/> .", content_type="text/turtle"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "shex_file", "This field is required.")

    def test_patient_export_includes_specific_shex_file(self):
        response = self.client.get(reverse("exportar_paciente", args=[self.paciente.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        archive = zipfile.ZipFile(io.BytesIO(response.content))
        names = archive.namelist()

        self.assertEqual(len(names), 2)
        self.assertTrue(any(name.endswith(".ttl") for name in names))
        self.assertTrue(any(name.endswith(".shex") for name in names))

        shex_name = next(name for name in names if name.endswith(".shex"))
        schema_text = archive.read(shex_name).decode("utf-8")
        self.assertIn("<PatientShape>", schema_text)
        self.assertNotIn("<ProcedureShape>", schema_text)

    def test_procedure_export_includes_only_procedure_resource_and_schema(self):
        response = self.client.get(reverse("export_procedure_rdf", args=[self.procedimiento.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        archive = zipfile.ZipFile(io.BytesIO(response.content))
        ttl_name = next(name for name in archive.namelist() if name.endswith(".ttl"))
        shex_name = next(name for name in archive.namelist() if name.endswith(".shex"))
        ttl_text = archive.read(ttl_name).decode("utf-8")
        schema_text = archive.read(shex_name).decode("utf-8")

        graph = Graph()
        graph.parse(data=ttl_text, format="turtle")

        self.assertTrue(list(graph.subjects(RDF.type, FHIR.Procedure)))
        self.assertFalse(list(graph.subjects(RDF.type, FHIR.Patient)))
        self.assertFalse(list(graph.subjects(RDF.type, FHIR.Practitioner)))
        self.assertIn("start = @<ProcedureShape>", schema_text)
        self.assertIn("<ProcedureShape>", schema_text)
        self.assertNotIn("<PatientShape>", schema_text)
        self.assertNotIn("<PractitionerShape>", schema_text)

    def test_exported_procedure_bundle_can_be_imported_for_existing_profile(self):
        response = self.client.get(reverse("export_procedure_rdf", args=[self.procedimiento.id]))
        ttl_bytes, shex_bytes = self._extract_bundle_files(response.content)

        Procedimiento.objects.all().delete()
        ProcedimientoCatalogo.objects.all().delete()

        import_response = self.client.post(
            reverse("import_data"),
            {
                "rdf_file": SimpleUploadedFile("procedimiento.ttl", ttl_bytes, content_type="text/turtle"),
                "shex_file": SimpleUploadedFile("procedimiento.shex", shex_bytes, content_type="text/plain"),
            },
        )

        self.assertRedirects(import_response, reverse("pacientes_list"))
        self.assertEqual(Paciente.objects.count(), 1)
        self.assertEqual(Practicante.objects.count(), 1)
        self.assertEqual(ProcedimientoCatalogo.objects.count(), 1)
        self.assertEqual(Procedimiento.objects.count(), 1)

        procedimiento = Procedimiento.objects.select_related("codigo", "paciente", "practicante").get()
        self.assertEqual(procedimiento.codigo.codigo, "ABC123")
        self.assertEqual(procedimiento.paciente.nombre, "Ana")
        self.assertEqual(procedimiento.practicante.nombre, "Marta")
        self.assertEqual(procedimiento.descripcion, "Revision y limpieza")

    def test_import_rejects_schema_that_is_not_hl7_fhir_compatible(self):
        response = self.client.get(reverse("exportar_paciente", args=[self.paciente.id]))
        ttl_bytes, _ = self._extract_bundle_files(response.content)

        Procedimiento.objects.all().delete()
        Paciente.objects.all().delete()

        invalid_schema = b"start = <BadShape>\n<BadShape> { <http://example.org/name> . }"
        import_response = self.client.post(
            reverse("import_data"),
            {
                "rdf_file": SimpleUploadedFile("paciente.ttl", ttl_bytes, content_type="text/turtle"),
                "shex_file": SimpleUploadedFile("paciente.shex", invalid_schema, content_type="text/plain"),
            },
        )

        self.assertEqual(import_response.status_code, 200)
        self.assertContains(import_response, "El archivo ShEx subido no declara el namespace HL7 FHIR esperado.")
        self.assertEqual(Paciente.objects.count(), 0)

    def _extract_bundle_files(self, response_content):
        archive = zipfile.ZipFile(io.BytesIO(response_content))
        ttl_name = next(name for name in archive.namelist() if name.endswith(".ttl"))
        shex_name = next(name for name in archive.namelist() if name.endswith(".shex"))
        return archive.read(ttl_name), archive.read(shex_name)
