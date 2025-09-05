from django import forms
from .models import Cliente, Solicitud
from django.core.exceptions import ValidationError
from datetime import date
from django.forms import CheckboxSelectMultiple

class ClienteForm(forms.ModelForm):
    """Formulario basado en el modelo Cliente."""
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nit': forms.TextInput(attrs={'placeholder': 'Nit del cliente'}),
            'telefono_fijo': forms.TextInput(attrs={'placeholder': 'Teléfono Fijo (opcional)'}),
            'categorias_certificar': CheckboxSelectMultiple(),
            'fecha_solicitud': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),

            # Puedes agregar más widgets aquí si es necesario.
        }

class SolicitudForm(forms.ModelForm):
    """Formulario para establecer la fecha de solicitud."""
    fecha_solicitud = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
        required=True
    )

    class Meta:
        model = Solicitud
        fields = ['fecha_solicitud']

    def clean_fecha_solicitud(self):
        fecha = self.cleaned_data.get('fecha_solicitud')
        if fecha and fecha > date.today():
            raise ValidationError("La fecha de solicitud no puede ser futura.")
        return fecha
