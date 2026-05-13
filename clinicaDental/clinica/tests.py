from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Paciente, Practicante, Procedimiento, ProcedimientoCatalogo


class NavigationViewsTests(TestCase):
    def test_root_redirects_to_dashboard(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))

    def test_dashboard_page_is_available_at_clinica_root(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clinica/index.html")
        self.assertContains(response, "Panel operativo")

    def test_legacy_panel_url_redirects_to_clinica_root(self):
        response = self.client.get("/clinica/panel/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))


class PatientProcedureFlowTests(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            estado_civil="U",
        )
        self.otro_paciente = Paciente.objects.create(
            nombre="Luis",
            apellido="Garcia",
            genero="male",
            telefono="987654321",
            fecha_nacimiento=date(1988, 6, 15),
            estado_civil="M",
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
        self.otro_catalogo = ProcedimientoCatalogo.objects.create(
            codigo="XYZ789",
            text="Extraccion simple",
        )
        self.procedimiento = Procedimiento.objects.create(
            codigo=self.catalogo,
            paciente=self.paciente,
            practicante=self.practicante,
            descripcion="Revision y limpieza",
            realizado_el=date(2026, 5, 10),
        )
        self.otro_procedimiento = Procedimiento.objects.create(
            codigo=self.otro_catalogo,
            paciente=self.otro_paciente,
            practicante=self.practicante,
            descripcion="Extraccion",
            realizado_el=date(2026, 5, 11),
        )

    def test_procedure_list_redirects_to_patients(self):
        response = self.client.get(reverse("procedimiento_list"))

        self.assertRedirects(response, reverse("pacientes_list"))

    def test_patient_detail_only_shows_its_procedures(self):
        response = self.client.get(reverse("paciente_detail", args=[self.paciente.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limpieza dental")
        self.assertNotContains(response, "Extraccion simple")
        self.assertContains(response, f"?paciente={self.paciente.id}")
        self.assertContains(
            response,
            f'data-href="{reverse("procedimiento_detail", args=[self.procedimiento.id])}"',
        )
        self.assertContains(
            response,
            f"onclick=\"window.location.href='{reverse('procedimiento_detail', args=[self.procedimiento.id])}'\"",
        )

    def test_patient_list_rows_are_navigable(self):
        response = self.client.get(reverse("pacientes_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'data-href="{reverse("paciente_detail", args=[self.paciente.id])}"',
        )
        self.assertContains(
            response,
            f"onclick=\"window.location.href='{reverse('paciente_detail', args=[self.paciente.id])}'\"",
        )

    def test_create_procedure_requires_patient_context(self):
        response = self.client.get(reverse("procedimiento_crear"))

        self.assertRedirects(response, reverse("pacientes_list"))

    def test_create_procedure_preselects_patient_and_redirects_back_to_detail(self):
        response = self.client.get(f"{reverse('procedimiento_crear')}?paciente={self.paciente.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["form"].fields["paciente"].queryset),
            [self.paciente],
        )

        post_response = self.client.post(
            reverse("procedimiento_crear"),
            {
                "paciente_context": self.paciente.id,
                "codigo": self.otro_catalogo.id,
                "codigo_text": self.otro_catalogo.codigo,
                "status": "completed",
                "paciente": self.paciente.id,
                "practicante": self.practicante.id,
                "diente": "",
                "descripcion": "Procedimiento nuevo",
                "realizado_el": "2026-05-13",
            },
        )

        self.assertRedirects(
            post_response,
            reverse("paciente_detail", args=[self.paciente.id]),
        )
        self.assertTrue(
            Procedimiento.objects.filter(
                paciente=self.paciente,
                descripcion="Procedimiento nuevo",
            ).exists()
        )
