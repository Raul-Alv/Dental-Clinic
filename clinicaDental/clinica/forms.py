from django import forms
from .models import Paciente, Practicante, Procedimiento, ProcedimientoCatalogo
from django.forms.models import ModelChoiceIteratorValue

# 1) Campo que muestra sólo .text en el select
class CatalogoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.text

# 2) Widget que añade a cada <option> el atributo data-code="<codigo>"
class CatalogoSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # genera la opción normalmente
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        # extrae el PK real, ya que `value` puede ser un ModelChoiceIteratorValue
        if isinstance(value, ModelChoiceIteratorValue):
            raw_pk = value.value
        else:
            raw_pk = value
        # inyecta data-code solo si hay PK
        if raw_pk not in (None, ''):
            try:
                cat = ProcedimientoCatalogo.objects.get(pk=raw_pk)
                option.setdefault('attrs', {})
                option['attrs']['data-code'] = cat.codigo
            except ProcedimientoCatalogo.DoesNotExist:
                pass
        return option

class ProcedimientoForm(forms.ModelForm):
    codigo = CatalogoModelChoiceField(
        queryset=ProcedimientoCatalogo.objects.all(),
        widget=CatalogoSelect(attrs={'class': 'form-control'}),
        label='Procedimiento'
    )
    # Campo de solo lectura para mostrar el código real
    codigo_text = forms.CharField(
        required=False,
        label='Código del Procedimiento',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = Procedimiento
        fields = [
            'codigo',
            'codigo_text',
            'status',
            'paciente',
            'practicante',
            'diente',
            'descripcion',
            'realizado_el',
        ]
        labels = {
            'status': 'Estado',
            'paciente': 'Paciente',
            'practicante': 'Practicante',
            'diente': 'Diente',
            'descripcion': 'Descripción',
            'realizado_el': 'Fecha de Realización',
        }
        widgets = {
            'codigo': CatalogoSelect(attrs={'class': 'form-control'}),
            'codigo_text': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'practicante': forms.Select(attrs={'class': 'form-control'}),
            'diente': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'realizado_el': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Precargar el valor del código en edición o post
        initial_codigo = None
        if self.instance and self.instance.pk:
            initial_codigo = self.instance.codigo.codigo
        else:
            initial_codigo = self.data.get('codigo') or self.initial.get('codigo')
            if initial_codigo:
                try:
                    initial_codigo = ProcedimientoCatalogo.objects.get(pk=initial_codigo).codigo
                except ProcedimientoCatalogo.DoesNotExist:
                    initial_codigo = ''
        self.fields['codigo_text'].initial = initial_codigo

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ['activo']
        labels = {
            'nombre': 'Nombre del Paciente',
            'apellido': 'Apellido del Paciente',
            'genero': 'Género',
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'calle': 'Dirección',
            'ciudad': 'Ciudad',
            'provincia': 'Provincia',
            'pais': 'País',
            'codigo_postal': 'Código Postal',
            'estado_civil': 'Estado Civil',
            
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Juan'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Alvarez'}),
            'genero': forms.Select(attrs={'class': 'form-control','placeholder': 'Género'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. 123456789'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control','type': 'date', 'placeholder': 'Fecha de Nacimiento'}),
            'calle': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Calle Uría 12'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Oviedo'}), 
            'provincia': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Asturias'}),
            'pais': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. España'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. 33001'}),
            'estado_civil': forms.Select(attrs={'class': 'form-control','placeholder': 'Estado Civil'}), 
        }

class PracticanteForm(forms.ModelForm):
    class Meta:
        model = Practicante
        exclude = ['activo']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellidos',
            'genero': 'Género',
            'telefono': 'Teléfono',
            'cualificacion': 'Culaificación',

            
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Juan'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Alvarez'}),
            'genero': forms.Select(attrs={'class': 'form-control','placeholder': 'Género'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. 123456789'}),
            'cualificacion': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. Licenciado en Odontología'}),
        }

class RDFUploadForm(forms.Form):
    rdf_file = forms.FileField(
        label="Archivo RDF",
        widget=forms.ClearableFileInput(attrs={'hidden': True, 'id': 'id_rdf_file'})
    )
         