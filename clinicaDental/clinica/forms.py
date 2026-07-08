from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelChoiceIteratorValue
from django.utils import timezone

from .models import Paciente, Practicante, Procedimiento, ProcedimientoCatalogo, StatusProcedimiento


def clean_phone_number(value):
    telefono = (value or "").strip()
    if telefono and (len(telefono) != 9 or not telefono.isdigit()):
        raise ValidationError("Debe tener 9 cifras numericas.")
    return telefono


class CatalogoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.text


class CatalogoSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if isinstance(value, ModelChoiceIteratorValue):
            raw_pk = value.value
        else:
            raw_pk = value

        if raw_pk not in (None, ""):
            try:
                catalogo = ProcedimientoCatalogo.objects.get(pk=raw_pk)
                option.setdefault("attrs", {})
                option["attrs"]["data-code"] = catalogo.codigo
            except ProcedimientoCatalogo.DoesNotExist:
                pass

        return option


class ProcedimientoForm(forms.ModelForm):
    REQUIRED_FIELDS = (
        "codigo",
        "status",
        "paciente",
        "practicante",
        "realizado_el",
    )
    OPTIONAL_FIELDS = (
        "diente",
        "descripcion",
    )

    codigo = CatalogoModelChoiceField(
        queryset=ProcedimientoCatalogo.objects.all(),
        widget=CatalogoSelect(attrs={"class": "form-control"}),
        label="Intervención",
    )
    codigo_text = forms.CharField(
        required=False,
        label="Codigo de la intervención",
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    )

    class Meta:
        model = Procedimiento
        fields = [
            "codigo",
            "codigo_text",
            "status",
            "paciente",
            "practicante",
            "diente",
            "descripcion",
            "realizado_el",
        ]
        labels = {
            "status": "Estado",
            "paciente": "Paciente",
            "practicante": "Practicante",
            "diente": "Pieza dental",
            "descripcion": "Descripción",
            "realizado_el": "Fecha de Realización",
        }
        widgets = {
            "codigo": CatalogoSelect(attrs={"class": "form-control"}),
            "codigo_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "paciente": forms.Select(attrs={"class": "form-control"}),
            "practicante": forms.Select(attrs={"class": "form-control"}),
            "diente": forms.Select(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "realizado_el": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, paciente_fijado=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_required_attribute = False

        for field_name in self.REQUIRED_FIELDS:
            field = self.fields[field_name]
            field.required = True
            field.error_messages["required"] = "Es obligatorio."
            field.widget.attrs["aria-required"] = "true"

        for field_name in self.OPTIONAL_FIELDS:
            field = self.fields[field_name]
            field.required = False
            field.widget.attrs.pop("aria-required", None)

        self.fields["paciente"].queryset = Paciente.objects.filter(activo=True)
        self.fields["practicante"].queryset = Practicante.objects.filter(activo=True)

        if paciente_fijado is not None:
            self.fields["paciente"].queryset = Paciente.objects.filter(id=paciente_fijado.id)
            self.fields["paciente"].initial = paciente_fijado
            self.fields["paciente"].empty_label = None

        is_new_instance = not self.instance or self.instance._state.adding
        if not self.is_bound and is_new_instance:
            self.initial.setdefault("status", StatusProcedimiento.DESCONOCIDO)
            self.initial.setdefault("realizado_el", timezone.localdate())

        initial_codigo = None
        if self.instance and not self.instance._state.adding:
            initial_codigo = self.instance.codigo.codigo
        else:
            selected_codigo = self.data.get("codigo") or self.initial.get("codigo")
            if selected_codigo:
                try:
                    initial_codigo = ProcedimientoCatalogo.objects.get(pk=selected_codigo).codigo
                except ProcedimientoCatalogo.DoesNotExist:
                    initial_codigo = ""

        self.fields["codigo_text"].initial = initial_codigo


class PacienteForm(forms.ModelForm):
    REQUIRED_FIELDS = (
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

    class Meta:
        model = Paciente
        exclude = ["activo"]
        labels = {
            "nombre": "Nombre",
            "apellido": "Apellido",
            "genero": "Género",
            "telefono": "Teléfono",
            "fecha_nacimiento": "Fecha de Nacimiento",
            "calle": "Dirección",
            "ciudad": "Ciudad",
            "provincia": "Provincia",
            "pais": "País",
            "codigo_postal": "Código Postal",
            "estado_civil": "Estado Civil",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Juan"}),
            "apellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Alvarez"}),
            "genero": forms.Select(attrs={"class": "form-control", "placeholder": "Género"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 123456789"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "placeholder": "Fecha de Nacimiento"}
            ),
            "calle": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Calle Uria 12"}),
            "ciudad": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Oviedo"}),
            "provincia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Asturias"}),
            "pais": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. España"}),
            "codigo_postal": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 33001"}),
            "estado_civil": forms.Select(attrs={"class": "form-control", "placeholder": "Estado Civil"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_required_attribute = False

        for field_name in self.REQUIRED_FIELDS:
            field = self.fields[field_name]
            field.required = True
            field.error_messages["required"] = "Es obligatorio."
            field.widget.attrs["aria-required"] = "true"

        if not self.is_bound:
            default_choices = {
                "genero": "unknown",
                "estado_civil": "UNK",
            }
            normalizers = {
                "genero": Paciente.normalizar_genero,
                "estado_civil": Paciente.normalizar_estado_civil,
            }

            for field_name, fallback_value in default_choices.items():
                valid_values = {choice_value for choice_value, _ in self.fields[field_name].choices}
                current_value = self.initial.get(field_name, getattr(self.instance, field_name, None))
                normalized_value = normalizers[field_name](current_value)
                self.initial[field_name] = normalized_value if normalized_value in valid_values else fallback_value

    def clean_telefono(self):
        return clean_phone_number(self.cleaned_data.get("telefono"))

    def clean_codigo_postal(self):
        codigo_postal = (self.cleaned_data.get("codigo_postal") or "").strip()
        if codigo_postal and len(codigo_postal) != 5:
            raise ValidationError("Debe tener 5 caracteres.")
        return codigo_postal


class PracticanteForm(forms.ModelForm):
    REQUIRED_FIELDS = (
        "nombre",
        "apellido",
        "genero",
        "telefono",
        "cualificacion",
    )

    class Meta:
        model = Practicante
        exclude = ["activo"]
        labels = {
            "nombre": "Nombre",
            "apellido": "Apellidos",
            "genero": "Género",
            "telefono": "Teléfono",
            "cualificacion": "Cualificación",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Juan"}),
            "apellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Alvarez"}),
            "genero": forms.Select(attrs={"class": "form-control", "placeholder": "Género"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 123456789"}),
            "cualificacion": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. Licenciado en Odontología"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_required_attribute = False

        for field_name in self.REQUIRED_FIELDS:
            field = self.fields[field_name]
            field.required = True
            field.error_messages["required"] = "Es obligatorio."
            field.widget.attrs["aria-required"] = "true"

    def clean_telefono(self):
        return clean_phone_number(self.cleaned_data.get("telefono"))


class RDFUploadForm(forms.Form):
    rdf_file = forms.FileField(
        label="Archivo RDF",
        widget=forms.ClearableFileInput(attrs={"hidden": True, "id": "id_rdf_file"}),
    )
    shex_file = forms.FileField(
        label="Archivo ShEx",
        widget=forms.ClearableFileInput(attrs={"hidden": True, "id": "id_shex_file"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        rdf_file = cleaned_data.get("rdf_file")
        shex_file = cleaned_data.get("shex_file")

        if rdf_file and not rdf_file.name.lower().endswith((".ttl", ".rdf")):
            self.add_error("rdf_file", "El archivo RDF debe tener extensión .ttl o .rdf.")

        if shex_file and not shex_file.name.lower().endswith((".shex", ".txt")):
            self.add_error("shex_file", "El archivo ShEx debe tener extensión .shex o .txt.")

        return cleaned_data
