from django.contrib import admin
from .models import PlanAuditoria, ActaAuditoria, AsistenteActa, ActividadCEA, HoraActividadPlan


# Inline para HoraActividadPlan
class HoraActividadPlanInline(admin.TabularInline):
    model = HoraActividadPlan
    extra = 1
    fields = ['fecha', 'hora', 'actividad', 'nombre_auditado', 'cargo_auditado']


class PlanAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['programacion', 'auditor', 'fecha_aprobacion', 'aprobado_por_cliente']
    list_filter = ['fecha_aprobacion', 'auditor', 'aprobado_por_cliente']
    inlines = [HoraActividadPlanInline]


@admin.register(HoraActividadPlan)
class HoraActividadPlanAdmin(admin.ModelAdmin):
    list_display = ['actividad', 'fecha', 'hora', 'nombre_auditado', 'cargo_auditado']
    list_filter = ['fecha', 'actividad__nivel']
    search_fields = ['nombre_auditado', 'cargo_auditado', 'actividad__descripcion']


# Registrar modelos
admin.site.register(PlanAuditoria, PlanAuditoriaAdmin)
admin.site.register(ActaAuditoria)
admin.site.register(AsistenteActa)
admin.site.register(ActividadCEA)
