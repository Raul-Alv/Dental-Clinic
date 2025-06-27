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
            'codigo': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej. PROC-001'}),
            'status': forms.Select(attrs={'class': 'form-control','placeholder': 'Ej. Pendiente'}),
            'paciente': forms.Select(attrs={'class': 'form-control','placeholder': 'Ej. Seleccionar Paciente'}),
            'practicante': forms.Select(attrs={'class': 'form-control','placeholder': 'Ej. Seleccionar Practicante'}),
            'diente': forms.Select(attrs={'class': 'form-control','placeholder': 'Ej. Seleccionar Diente'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Descripción del Procedimiento'}),
            'realizado_el': forms.DateInput(attrs={'class': 'form-control','type': 'date', 'placeholder': 'Ej. Fecha de Realización'}),
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
         