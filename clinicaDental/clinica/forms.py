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
        