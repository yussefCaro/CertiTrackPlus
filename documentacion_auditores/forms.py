from django import forms
from .models import PlanAuditoria, ActaAuditoria, AsistenteActa, HoraActividadPlan

class PlanAuditoriaForm(forms.ModelForm):
    class Meta:
        model = PlanAuditoria
        fields = ['iaf_md4_verificado', 'observaciones', 'archivo_vehiculos_instructores']

class ActaAuditoriaForm(forms.ModelForm):
    class Meta:
        model = ActaAuditoria
        fields = [
            'representante_legal_nombre',
            'representante_legal_cargo',
            'firma_representante',
            'firma_auditor',
            'fecha_inicio',
            'fecha_cierre',
            'universo_normal',
            'poblacion_normal',
            'muestra_normal',
            'universo_reducido',
            'poblacion_reducido',
            'muestra_reducido',
            'aspectos_relevantes',
            'conclusiones_etapa1',
            'quejas_registradas',
            'conclusiones_etapa2',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'representante_legal_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'representante_legal_cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'universo_normal': forms.NumberInput(attrs={'class': 'form-control'}),
            'poblacion_normal': forms.NumberInput(attrs={'class': 'form-control'}),
            'muestra_normal': forms.NumberInput(attrs={'class': 'form-control'}),
            'universo_reducido': forms.NumberInput(attrs={'class': 'form-control'}),
            'poblacion_reducido': forms.NumberInput(attrs={'class': 'form-control'}),
            'muestra_reducido': forms.NumberInput(attrs={'class': 'form-control'}),
            'aspectos_relevantes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describa aquí los aspectos relevantes observados durante la auditoría',
                'class': 'form-control',
            }),
            'conclusiones_etapa1': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describa aquí las conclusiones de la etapa 1',
                'class': 'form-control',
            }),
            'quejas_registradas': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describa aquí las quejas registradas',
                'class': 'form-control',
            }),
            'conclusiones_etapa2': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describa aquí las conclusiones de la etapa 2',
                'class': 'form-control',
            }),
            # Si ‘firma_representante’ y ‘firma_auditor’ son ImageField/FileField:
            'firma_representante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'firma_auditor': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class AsistenteActaForm(forms.ModelForm):
    class Meta:
        model = AsistenteActa
        fields = ['nombre', 'cargo']
        exclude = ['firma_apertura', 'firma_cierre']  # si existen y no se editan aquí
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django.forms import modelformset_factory

HoraActividadPlanFormSet = modelformset_factory(
    HoraActividadPlan,
    fields=('fecha', 'hora', 'actividad', 'nombre_auditado', 'cargo_auditado'),
    extra=1,
    widgets={
        'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        'actividad': forms.TextInput(attrs={'class': 'form-control'}),
        'nombre_auditado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
        'cargo_auditado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo o posición'})
    }
)
