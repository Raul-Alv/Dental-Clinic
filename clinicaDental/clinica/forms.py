from django import forms
from django.forms.models import ModelChoiceIteratorValue

from .models import Paciente, Practicante, Procedimiento, ProcedimientoCatalogo


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
    codigo = CatalogoModelChoiceField(
        queryset=ProcedimientoCatalogo.objects.all(),
        widget=CatalogoSelect(attrs={"class": "form-control"}),
        label="Procedimiento",
    )
    codigo_text = forms.CharField(
        required=False,
        label="Codigo del Procedimiento",
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
            "diente": "Diente",
            "descripcion": "Descripcion",
            "realizado_el": "Fecha de Realizacion",
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
        self.fields["paciente"].queryset = Paciente.objects.filter(activo=True)
        self.fields["practicante"].queryset = Practicante.objects.filter(activo=True)

        if paciente_fijado is not None:
            self.fields["paciente"].queryset = Paciente.objects.filter(id=paciente_fijado.id)
            self.fields["paciente"].initial = paciente_fijado
            self.fields["paciente"].empty_label = None

        initial_codigo = None
        if self.instance and self.instance.pk:
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
    class Meta:
        model = Paciente
        exclude = ["activo"]
        labels = {
            "nombre": "Nombre del Paciente",
            "apellido": "Apellido del Paciente",
            "genero": "Genero",
            "telefono": "Telefono",
            "fecha_nacimiento": "Fecha de Nacimiento",
            "calle": "Direccion",
            "ciudad": "Ciudad",
            "provincia": "Provincia",
            "pais": "Pais",
            "codigo_postal": "Codigo Postal",
            "estado_civil": "Estado Civil",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Juan"}),
            "apellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Alvarez"}),
            "genero": forms.Select(attrs={"class": "form-control", "placeholder": "Genero"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 123456789"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "placeholder": "Fecha de Nacimiento"}
            ),
            "calle": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Calle Uria 12"}),
            "ciudad": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Oviedo"}),
            "provincia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Asturias"}),
            "pais": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Espana"}),
            "codigo_postal": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 33001"}),
            "estado_civil": forms.Select(attrs={"class": "form-control", "placeholder": "Estado Civil"}),
        }


class PracticanteForm(forms.ModelForm):
    class Meta:
        model = Practicante
        exclude = ["activo"]
        labels = {
            "nombre": "Nombre",
            "apellido": "Apellidos",
            "genero": "Genero",
            "telefono": "Telefono",
            "cualificacion": "Cualificacion",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Juan"}),
            "apellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Alvarez"}),
            "genero": forms.Select(attrs={"class": "form-control", "placeholder": "Genero"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 123456789"}),
            "cualificacion": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. Licenciado en Odontologia"}
            ),
        }


class RDFUploadForm(forms.Form):
    rdf_file = forms.FileField(
        label="Archivo RDF",
        widget=forms.ClearableFileInput(attrs={"hidden": True, "id": "id_rdf_file"}),
    )
