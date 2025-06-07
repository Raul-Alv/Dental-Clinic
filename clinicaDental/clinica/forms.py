from django import forms
from .models import Paciente, Practicante, Procedimiento, Diente

class ProcedimientoForm(forms.ModelForm):
    class Meta:
        model = Procedimiento
        fields = '__all__'
        labels = {
            'codigo': 'Código del Procedimiento',
            'status': 'Estado',
            'paciente': 'Paciente',
            'practicante': 'Practicante',
            'diente': 'Diente',
            'descripcion': 'Descripción',
            'realizado_el': 'Fecha de Realización',
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Código del Procedimiento'}),
            'status': forms.Select(attrs={'placeholder': 'Estado del Procedimiento'}),
            'paciente': forms.Select(attrs={'placeholder': 'Seleccionar Paciente'}),
            'practicante': forms.Select(attrs={'placeholder': 'Seleccionar Practicante'}),
            'diente': forms.Select(attrs={'placeholder': 'Seleccionar Diente'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripción del Procedimiento'}),
            'realizado_el': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha de Realización'}),
        }

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
            'direccion': 'Dirección',
            'estado_civil': 'Estado Civil',
            
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del Paciente'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Apellido del Paciente'}),
            'genero': forms.Select(attrs={'placeholder': 'Género'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha de Nacimiento'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección'}),
            'estado_civil': forms.Select(attrs={'placeholder': 'Estado Civil'}), 
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
            'nombre': forms.TextInput(attrs={'placeholder': 'Juan'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Alvarez'}),
            'genero': forms.Select(attrs={'placeholder': 'Género'}),
            'telefono': forms.TextInput(attrs={'placeholder': '123456789'}),
            'cualificacion': forms.TextInput(attrs={'placeholder': 'Dentista'}),
        }

class RDFUploadForm(forms.Form):
    rdf_file = forms.FileField(label="Archivo RDF")
         