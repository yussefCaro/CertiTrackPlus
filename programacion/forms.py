from django import forms
from .models import ProgramacionAuditoria, Auditor, FechaEtapa2
from django.forms.models import inlineformset_factory

class ProgramacionAuditoriaForm(forms.ModelForm):
    auditores = forms.ModelChoiceField(
        queryset=Auditor.objects.all(),
        empty_label="Seleccione un auditor",
        required=True
    )
    fecha_programacion_etapa1 = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    hora_etapa1 = forms.TimeField(  # 📌 Agregamos el widget para selector de hora
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True
    )

    class Meta:
        model = ProgramacionAuditoria
        exclude = ['cotizacion']

class FechaEtapa2Form(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora = forms.TimeField(  # 📌 También aquí agregamos el selector de hora
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True
    )

    class Meta:
        model = FechaEtapa2
        fields = ['fecha', 'hora']

FechaEtapa2FormSet = inlineformset_factory(
    ProgramacionAuditoria,
    FechaEtapa2,
    form=FechaEtapa2Form,
    extra=1,
    max_num=3
)
