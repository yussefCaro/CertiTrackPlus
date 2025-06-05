from django.contrib import admin
from .models import ProgramacionAuditoria, NivelAuditoriaCEA, Auditor, FechaEtapa2

class FechaEtapa2Inline(admin.TabularInline):  # Puedes usar StackedInline si prefieres una vista en bloque
    model = FechaEtapa2
    extra = 1  # Número de filas vacías que aparecerán para agregar registros nuevos

@admin.register(ProgramacionAuditoria)
class ProgramacionAuditoriaAdmin(admin.ModelAdmin):
    inlines = [FechaEtapa2Inline]  # Agrega los campos de etapa 2 dentro de la programación
    list_display = ('cotizacion', 'nivel_auditoria', 'fecha_programacion_etapa1', 'hora_etapa1', 'estado')

admin.site.register(NivelAuditoriaCEA)
admin.site.register(Auditor)

