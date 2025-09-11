from django import forms
from .models import PlanAuditoria, ActaAuditoria, AsistenteActa, HoraActividadPlan

class PlanAuditoriaForm(forms.ModelForm):
    class Meta:
        model = PlanAuditoria
        fields = ['iaf_md4_verificado', 'observaciones', 'archivo_vehiculos_instructores']

class ActaAuditoriaForm(forms.ModelForm):
    class Meta:
        model = ActaAuditoria
        fields = ['representante_legal_nombre', 'representante_legal_cargo',
                  'firma_representante', 'firma_auditor', 'fecha_inicio', 'fecha_cierre',
                  'aspectos_relevantes',
                  'universo_normal', 'poblacion_normal', 'muestra_normal',
                  'universo_reducido', 'poblacion_reducido', 'muestra_reducido']
        widgets = {
            'aspectos_relevantes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describa aquí los aspectos relevantes observados durante la auditoría',
                'class': 'form-control'
            }),
        }

class AsistenteActaForm(forms.ModelForm):
    class Meta:
        model = AsistenteActa
        fields = ['nombre', 'cargo']
        exclude = ['firma_apertura', 'firma_cierre']

# FormSet ACTUALIZADO para incluir los nuevos campos
from django.forms import modelformset_factory

HoraActividadPlanFormSet = modelformset_factory(
    HoraActividadPlan,
    fields=('fecha', 'hora', 'actividad', 'nombre_auditado', 'cargo_auditado'),  # ← CAMPOS AGREGADOS
    extra=1,
    widgets={
        'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        'nombre_auditado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
        'cargo_auditado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo o posición'})
    }
)
