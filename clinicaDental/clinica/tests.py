from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import PacienteForm, PracticanteForm, ProcedimientoForm
from .models import Diente, Paciente, Practicante, Procedimiento, ProcedimientoCatalogo


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


class PacienteFormTests(TestCase):
    def test_patient_form_uses_unknown_as_default_for_choice_fields(self):
        form = PacienteForm()

        self.assertEqual(form.initial["genero"], "unknown")
        self.assertEqual(form.initial["estado_civil"], "UNK")

    def test_patient_form_requires_requested_fields_with_custom_message(self):
        form = PacienteForm(data={})

        self.assertFalse(form.is_valid())

        required_fields = (
            "nombre",
            "apellido",
            "genero",
            "telefono",
            "fecha_nacimiento",
            "calle",
            "ciudad",
            "provincia",
            "codigo_postal",
            "pais",
            "estado_civil",
        )

        for field_name in required_fields:
            self.assertTrue(form.fields[field_name].required)
            self.assertEqual(form.errors[field_name], ["Es obligatorio."])

    def test_patient_form_validates_phone_with_exactly_nine_digits(self):
        form = PacienteForm(
            data={
                "nombre": "Ana",
                "apellido": "Lopez",
                "genero": "unknown",
                "telefono": "1234",
                "fecha_nacimiento": "1990-01-01",
                "calle": "Calle Mayor 1",
                "ciudad": "Oviedo",
                "provincia": "Asturias",
                "pais": "Espana",
                "codigo_postal": "33001",
                "estado_civil": "UNK",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["telefono"], ["Debe tener 9 cifras numericas."])

    def test_patient_form_rejects_non_numeric_phone(self):
        form = PacienteForm(
            data={
                "nombre": "Ana",
                "apellido": "Lopez",
                "genero": "unknown",
                "telefono": "12345abcd",
                "fecha_nacimiento": "1990-01-01",
                "calle": "Calle Mayor 1",
                "ciudad": "Oviedo",
                "provincia": "Asturias",
                "pais": "Espana",
                "codigo_postal": "33001",
                "estado_civil": "UNK",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["telefono"], ["Debe tener 9 cifras numericas."])

    def test_patient_form_validates_postal_code_length(self):
        form = PacienteForm(
            data={
                "nombre": "Ana",
                "apellido": "Lopez",
                "genero": "unknown",
                "telefono": "123456789",
                "fecha_nacimiento": "1990-01-01",
                "calle": "Calle Mayor 1",
                "ciudad": "Oviedo",
                "provincia": "Asturias",
                "pais": "Espana",
                "codigo_postal": "3300",
                "estado_civil": "UNK",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["codigo_postal"], ["Debe tener 5 caracteres."])


class PacienteNormalizationTests(TestCase):
    def test_patient_masks_id_except_last_two_digits(self):
        paciente = Paciente(id=123456789012)

        self.assertEqual(paciente.id_enmascarado, "**********12")

    def test_patient_generates_social_security_number_as_id(self):
        paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="F",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            estado_civil="S",
        )

        self.assertEqual(len(str(paciente.id)), 12)
        self.assertTrue(Paciente.es_numero_seguridad_social_valido(paciente.id))

    def test_patient_save_normalizes_rdf_codes(self):
        paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="F",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            estado_civil="S",
        )

        self.assertEqual(paciente.genero, "female")
        self.assertEqual(paciente.estado_civil, "U")

    def test_patient_labels_translate_legacy_rdf_codes(self):
        paciente = Paciente(
            nombre="Luis",
            apellido="Garcia",
            genero="M",
            telefono="123456789",
            fecha_nacimiento=date(1988, 6, 15),
            estado_civil="C",
        )

        self.assertEqual(paciente.genero_label, "Masculino")
        self.assertEqual(paciente.estado_civil_label, "Casado")

    def test_patient_form_normalizes_legacy_rdf_values(self):
        paciente = Paciente(genero="F", estado_civil="S")

        form = PacienteForm(instance=paciente)

        self.assertEqual(form.initial["genero"], "female")
        self.assertEqual(form.initial["estado_civil"], "U")


class ProcedimientoFormTests(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
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

    def test_procedure_form_uses_unknown_status_and_today_as_defaults(self):
        form = ProcedimientoForm(paciente_fijado=self.paciente)

        self.assertEqual(form.initial["status"], "unknown")
        self.assertEqual(form.initial["realizado_el"], timezone.localdate())

    def test_procedure_form_requires_requested_fields_with_custom_message(self):
        form = ProcedimientoForm(data={}, paciente_fijado=self.paciente)

        self.assertFalse(form.is_valid())

        required_fields = (
            "codigo",
            "status",
            "paciente",
            "practicante",
            "diente",
            "descripcion",
            "realizado_el",
        )

        for field_name in required_fields:
            self.assertTrue(form.fields[field_name].required)
            self.assertEqual(form.errors[field_name], ["Es obligatorio."])


class PracticanteFormTests(TestCase):
    def test_practitioner_form_requires_all_fields_with_custom_message(self):
        form = PracticanteForm(data={})

        self.assertFalse(form.is_valid())

        required_fields = (
            "nombre",
            "apellido",
            "genero",
            "telefono",
            "cualificacion",
        )

        for field_name in required_fields:
            self.assertTrue(form.fields[field_name].required)
            self.assertEqual(form.errors[field_name], ["Es obligatorio."])

    def test_practitioner_create_view_shows_required_messages_when_fields_are_empty(self):
        response = self.client.post(
            reverse("practicantes_crear"),
            {
                "nombre": "",
                "apellido": "",
                "genero": "",
                "telefono": "",
                "cualificacion": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="required-indicator" aria-hidden="true">*</span>', html=True)
        self.assertContains(response, "Es obligatorio.", count=5)

    def test_practitioner_form_validates_phone_with_exactly_nine_digits(self):
        form = PracticanteForm(
            data={
                "nombre": "Marta",
                "apellido": "Sanz",
                "genero": "F",
                "telefono": "1234",
                "cualificacion": "Odontologa",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["telefono"], ["Debe tener 9 cifras numericas."])

    def test_practitioner_form_rejects_non_numeric_phone(self):
        form = PracticanteForm(
            data={
                "nombre": "Marta",
                "apellido": "Sanz",
                "genero": "F",
                "telefono": "12345abcd",
                "cualificacion": "Odontologa",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["telefono"], ["Debe tener 9 cifras numericas."])


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
        self.diente = Diente.objects.create(
            codigo="T-11",
            display="Incisivo central superior derecho",
            definicion="Incisivo central superior derecho",
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

    def test_patient_detail_uses_full_labels_for_legacy_rdf_codes(self):
        Paciente.objects.filter(id=self.paciente.id).update(genero="F", estado_civil="S")

        response = self.client.get(reverse("paciente_detail", args=[self.paciente.id]))

        self.assertContains(response, "Femenino")
        self.assertContains(response, "Soltero")

    def test_patient_list_rows_are_navigable(self):
        response = self.client.get(reverse("pacientes_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"ID {self.paciente.id_enmascarado}")
        self.assertNotContains(response, f"ID {self.paciente.id}")
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
        self.assertEqual(response.context["form"].initial["status"], "unknown")
        self.assertEqual(response.context["form"].initial["realizado_el"], timezone.localdate())

        post_response = self.client.post(
            reverse("procedimiento_crear"),
            {
                "paciente_context": self.paciente.id,
                "codigo": self.otro_catalogo.id,
                "codigo_text": self.otro_catalogo.codigo,
                "status": "completed",
                "paciente": self.paciente.id,
                "practicante": self.practicante.id,
                "diente": self.diente.id,
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

    def test_create_procedure_shows_required_messages_when_fields_are_empty(self):
        response = self.client.post(
            reverse("procedimiento_crear"),
            {
                "paciente_context": self.paciente.id,
                "codigo": "",
                "codigo_text": "",
                "status": "",
                "paciente": "",
                "practicante": "",
                "diente": "",
                "descripcion": "",
                "realizado_el": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="required-indicator" aria-hidden="true">*</span>', html=True)
        self.assertContains(response, "Es obligatorio.", count=7)


class DashboardOverviewTests(TestCase):
    def setUp(self):
        self.paciente_activo = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            estado_civil="U",
        )
        self.paciente_inactivo = Paciente.objects.create(
            activo=False,
            nombre="Luis",
            apellido="Garcia",
            genero="male",
            telefono="987654321",
            fecha_nacimiento=date(1988, 6, 15),
            estado_civil="M",
        )
        self.practicante_activo = Practicante.objects.create(
            nombre="Marta",
            apellido="Sanz",
            genero="F",
            telefono="123123123",
            cualificacion="Odontologa",
        )
        self.practicante_inactivo = Practicante.objects.create(
            activo=False,
            nombre="Diego",
            apellido="Suarez",
            genero="M",
            telefono="456456456",
            cualificacion="Cirujano oral",
        )
        self.catalogos = [
            ProcedimientoCatalogo.objects.create(codigo=f"PROC{i}", text=f"Procedimiento {i}")
            for i in range(1, 6)
        ]
        self.procedimientos_activos = [
            Procedimiento.objects.create(
                codigo=self.catalogos[0],
                paciente=self.paciente_activo,
                practicante=self.practicante_activo,
                descripcion="Procedimiento reciente 1",
                realizado_el=date(2026, 5, 10),
                status="completed",
            ),
            Procedimiento.objects.create(
                codigo=self.catalogos[1],
                paciente=self.paciente_activo,
                practicante=self.practicante_activo,
                descripcion="Procedimiento reciente 2",
                realizado_el=date(2026, 5, 11),
                status="completed",
            ),
            Procedimiento.objects.create(
                codigo=self.catalogos[2],
                paciente=self.paciente_activo,
                practicante=self.practicante_activo,
                descripcion="Procedimiento reciente 3",
                realizado_el=date(2026, 5, 12),
                status="completed",
            ),
            Procedimiento.objects.create(
                codigo=self.catalogos[3],
                paciente=self.paciente_activo,
                practicante=self.practicante_activo,
                descripcion="Procedimiento reciente 4",
                realizado_el=date(2026, 5, 13),
                status="completed",
            ),
        ]
        self.procedimiento_excluido = Procedimiento.objects.create(
            codigo=self.catalogos[4],
            paciente=self.paciente_inactivo,
            practicante=self.practicante_inactivo,
            descripcion="No deberia aparecer",
            realizado_el=date(2026, 5, 20),
            status="completed",
        )

    def test_dashboard_counts_only_active_records_and_limits_recent_items(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pacientes_count"], 1)
        self.assertEqual(response.context["practicantes_count"], 1)
        self.assertEqual(response.context["procedimientos_count"], 4)

        recent_ids = [procedimiento.id for procedimiento in response.context["recent_procedimientos"]]
        expected_ids = [
            self.procedimientos_activos[3].id,
            self.procedimientos_activos[2].id,
            self.procedimientos_activos[1].id,
        ]

        self.assertEqual(recent_ids, expected_ids)
        self.assertNotIn(self.procedimiento_excluido.id, recent_ids)


class ProcedimientoFormBehaviorTests(TestCase):
    def setUp(self):
        self.paciente_activo = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            estado_civil="U",
        )
        Paciente.objects.create(
            activo=False,
            nombre="Luis",
            apellido="Garcia",
            genero="male",
            telefono="987654321",
            fecha_nacimiento=date(1988, 6, 15),
            estado_civil="M",
        )
        self.practicante_activo = Practicante.objects.create(
            nombre="Marta",
            apellido="Sanz",
            genero="F",
            telefono="123123123",
            cualificacion="Odontologa",
        )
        Practicante.objects.create(
            activo=False,
            nombre="Diego",
            apellido="Suarez",
            genero="M",
            telefono="456456456",
            cualificacion="Cirujano oral",
        )
        self.catalogo = ProcedimientoCatalogo.objects.create(
            codigo="ABC123",
            text="Limpieza dental",
        )
        self.otro_catalogo = ProcedimientoCatalogo.objects.create(
            codigo="XYZ789",
            text="Extraccion simple",
        )
        self.diente = Diente.objects.create(
            codigo="T-11",
            display="Incisivo central superior derecho",
            definicion="Incisivo central superior derecho",
        )
        self.procedimiento = Procedimiento.objects.create(
            codigo=self.catalogo,
            paciente=self.paciente_activo,
            practicante=self.practicante_activo,
            diente=self.diente,
            descripcion="Revision y limpieza",
            realizado_el=date(2026, 5, 10),
            status="completed",
        )

    def test_procedure_form_limits_patient_and_practitioner_choices_to_active_records(self):
        form = ProcedimientoForm(paciente_fijado=self.paciente_activo)

        self.assertEqual(list(form.fields["paciente"].queryset), [self.paciente_activo])
        self.assertEqual(list(form.fields["practicante"].queryset), [self.practicante_activo])
        self.assertIn('data-code="ABC123"', str(form["codigo"]))
        self.assertIn('data-code="XYZ789"', str(form["codigo"]))

    def test_procedure_form_uses_instance_catalog_code_in_readonly_field(self):
        form = ProcedimientoForm(instance=self.procedimiento, paciente_fijado=self.paciente_activo)

        self.assertEqual(form.fields["codigo_text"].initial, self.catalogo.codigo)

    def test_procedure_form_uses_selected_catalog_code_when_bound(self):
        form = ProcedimientoForm(
            data={"codigo": str(self.otro_catalogo.id)},
            paciente_fijado=self.paciente_activo,
        )

        self.assertEqual(form.fields["codigo_text"].initial, self.otro_catalogo.codigo)


class PacienteCrudViewTests(TestCase):
    def _patient_payload(self, **overrides):
        payload = {
            "nombre": "Lucia",
            "apellido": "Martin",
            "genero": "female",
            "telefono": "123456789",
            "fecha_nacimiento": "1995-02-10",
            "calle": "Calle Mayor 1",
            "ciudad": "Oviedo",
            "provincia": "Asturias",
            "codigo_postal": "33001",
            "pais": "Espana",
            "estado_civil": "U",
        }
        payload.update(overrides)
        return payload

    def test_create_patient_creates_active_record_and_redirects_to_list(self):
        response = self.client.post(
            reverse("pacientes_crear"),
            self._patient_payload(),
        )

        self.assertRedirects(response, reverse("pacientes_list"))

        paciente = Paciente.objects.get(nombre="Lucia", apellido="Martin")
        self.assertTrue(paciente.activo)
        self.assertTrue(Paciente.es_numero_seguridad_social_valido(paciente.id))
        self.assertEqual(paciente.genero, "female")
        self.assertEqual(paciente.estado_civil, "U")

    def test_update_patient_persists_changes_and_redirects(self):
        paciente = Paciente.objects.create(
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

        response = self.client.post(
            reverse("paciente_update", args=[paciente.id]),
            self._patient_payload(
                nombre="Ana Maria",
                apellido="Lopez",
                genero="male",
                telefono="111222333",
                fecha_nacimiento="1990-01-01",
                calle="Avenida del Mar 20",
                ciudad="Gijon",
                provincia="Asturias",
                codigo_postal="33201",
                pais="Espana",
                estado_civil="M",
            ),
        )

        self.assertRedirects(response, reverse("pacientes_list"))

        paciente.refresh_from_db()
        self.assertEqual(paciente.nombre, "Ana Maria")
        self.assertEqual(paciente.genero, "male")
        self.assertEqual(paciente.telefono, "111222333")
        self.assertEqual(paciente.ciudad, "Gijon")
        self.assertEqual(paciente.estado_civil, "M")

    def test_delete_patient_soft_deletes_record_and_hides_it_from_list(self):
        paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            estado_civil="U",
        )
        visible_patient = Paciente.objects.create(
            nombre="Luis",
            apellido="Garcia",
            genero="male",
            telefono="987654321",
            fecha_nacimiento=date(1988, 6, 15),
            estado_civil="M",
        )

        response = self.client.post(reverse("paciente_delete", args=[paciente.id]))

        self.assertRedirects(response, reverse("pacientes_list"))

        paciente.refresh_from_db()
        self.assertFalse(paciente.activo)

        list_response = self.client.get(reverse("pacientes_list"))
        self.assertNotContains(list_response, str(paciente))
        self.assertContains(list_response, str(visible_patient))


class PracticanteCrudViewTests(TestCase):
    def _practitioner_payload(self, **overrides):
        payload = {
            "nombre": "Marta",
            "apellido": "Sanz",
            "genero": "F",
            "telefono": "123123123",
            "cualificacion": "Odontologa",
        }
        payload.update(overrides)
        return payload

    def test_create_practitioner_creates_active_record_and_redirects_to_list(self):
        response = self.client.post(
            reverse("practicantes_crear"),
            self._practitioner_payload(),
        )

        self.assertRedirects(response, reverse("practicantes_list"))

        practicante = Practicante.objects.get(nombre="Marta", apellido="Sanz")
        self.assertTrue(practicante.activo)

    def test_update_practitioner_persists_changes_and_redirects(self):
        practicante = Practicante.objects.create(
            nombre="Marta",
            apellido="Sanz",
            genero="F",
            telefono="123123123",
            cualificacion="Odontologa",
        )

        response = self.client.post(
            reverse("practicante_update", args=[practicante.id]),
            self._practitioner_payload(
                nombre="Mario",
                apellido="Sanz",
                genero="M",
                telefono="999888777",
                cualificacion="Cirujano oral",
            ),
        )

        self.assertRedirects(response, reverse("practicantes_list"))

        practicante.refresh_from_db()
        self.assertEqual(practicante.nombre, "Mario")
        self.assertEqual(practicante.genero, "M")
        self.assertEqual(practicante.telefono, "999888777")
        self.assertEqual(practicante.cualificacion, "Cirujano oral")

    def test_delete_practitioner_soft_deletes_record_and_hides_it_from_list(self):
        practicante = Practicante.objects.create(
            nombre="Marta",
            apellido="Sanz",
            genero="F",
            telefono="123123123",
            cualificacion="Odontologa",
        )
        visible_practitioner = Practicante.objects.create(
            nombre="Diego",
            apellido="Suarez",
            genero="M",
            telefono="456456456",
            cualificacion="Cirujano oral",
        )

        response = self.client.post(reverse("practicante_delete", args=[practicante.id]))

        self.assertRedirects(response, reverse("practicantes_list"))

        practicante.refresh_from_db()
        self.assertFalse(practicante.activo)

        list_response = self.client.get(reverse("practicantes_list"))
        self.assertNotContains(list_response, practicante.nombre)
        self.assertContains(list_response, visible_practitioner.nombre)


class ProcedimientoCrudViewTests(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            genero="female",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
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
        self.otro_catalogo = ProcedimientoCatalogo.objects.create(
            codigo="XYZ789",
            text="Extraccion simple",
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
            descripcion="Revision y limpieza",
            realizado_el=date(2026, 5, 10),
            status="completed",
        )

    def test_update_procedure_persists_changes_and_redirects_to_patient_detail(self):
        response = self.client.post(
            reverse("procedimiento_update", args=[self.procedimiento.id]),
            {
                "codigo": self.otro_catalogo.id,
                "codigo_text": self.otro_catalogo.codigo,
                "status": "on-hold",
                "paciente": self.paciente.id,
                "practicante": self.practicante.id,
                "diente": self.diente.id,
                "descripcion": "Procedimiento actualizado",
                "realizado_el": "2026-05-14",
            },
        )

        self.assertRedirects(response, reverse("paciente_detail", args=[self.paciente.id]))

        self.procedimiento.refresh_from_db()
        self.assertEqual(self.procedimiento.codigo, self.otro_catalogo)
        self.assertEqual(self.procedimiento.status, "on-hold")
        self.assertEqual(self.procedimiento.diente, self.diente)
        self.assertEqual(self.procedimiento.descripcion, "Procedimiento actualizado")
        self.assertEqual(self.procedimiento.realizado_el, date(2026, 5, 14))

    def test_delete_procedure_removes_record_and_redirects_to_patient_detail(self):
        response = self.client.post(reverse("procedimiento_delete", args=[self.procedimiento.id]))

        self.assertRedirects(response, reverse("paciente_detail", args=[self.paciente.id]))
        self.assertFalse(Procedimiento.objects.filter(id=self.procedimiento.id).exists())


class HistorialExportViewTests(TestCase):
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
            status="completed",
        )
        Procedimiento.objects.create(
            codigo=self.otro_catalogo,
            paciente=self.otro_paciente,
            practicante=self.practicante,
            descripcion="Extraccion",
            realizado_el=date(2026, 5, 11),
            status="completed",
        )

    def test_history_export_view_filters_procedures_by_selected_patient(self):
        response = self.client.get(
            reverse("export_historial"),
            {"paciente": self.paciente.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_paciente"], self.paciente)
        self.assertEqual(list(response.context["procedimientos"]), [self.procedimiento])
        self.assertContains(response, "Limpieza dental")
        self.assertNotContains(response, "Extraccion simple")
        self.assertContains(response, reverse("export_historial", args=[self.paciente.id]))
