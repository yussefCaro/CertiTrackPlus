from django.db import models
from django.contrib.auth.models import User
from programacion.models import ProgramacionAuditoria, NivelAuditoriaCEA

class PlanAuditoria(models.Model):
    programacion = models.OneToOneField(ProgramacionAuditoria, on_delete=models.CASCADE)
    auditor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': "Auditores"})
    iaf_md4_verificado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    fecha_aprobacion = models.DateField()  # Automáticamente, puede ser 2 días antes de etapa 2
    archivo_vehiculos_instructores = models.FileField(upload_to='documentacion/vehiculos_instructores/', null=True, blank=True)
    aprobado_por_cliente = models.BooleanField(default=False)
    fecha_aprobacion_cliente = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Plan Auditoría - {self.programacion.cotizacion.numero_servicio}"

class ActaAuditoria(models.Model):
    plan = models.OneToOneField(PlanAuditoria, on_delete=models.CASCADE, related_name='acta')
    representante_legal_nombre = models.CharField(max_length=255)
    representante_legal_cargo = models.CharField(max_length=100)
    firma_representante = models.ImageField(upload_to='documentacion/firmas/', null=True, blank=True)
    firma_auditor = models.ImageField(upload_to='documentacion/firmas/', null=True, blank=True)
    asistencia = models.TextField(help_text="Lista de asistentes con nombre, cargo y firmas")
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField(null=True, blank=True)
    fecha_inicio_subsanacion = models.DateField(null=True, blank=True)
    recomendaciones = models.CharField(max_length=200, blank=True)
    aspectos_relevantes = models.TextField("Aspectos relevantes del servicio auditado", blank=True)
    universo_normal = models.PositiveIntegerField("Universo (Normal)", default=0)
    poblacion_normal = models.PositiveIntegerField("Población (Normal)", default=0)
    muestra_normal = models.PositiveIntegerField("Muestra (Normal)", default=0)
    universo_reducido = models.PositiveIntegerField("Universo (Reducido)", default=0)
    poblacion_reducido = models.PositiveIntegerField("Población (Reducido)", default=0)
    muestra_reducido = models.PositiveIntegerField("Muestra (Reducido)", default=0)

    def __str__(self):
        return f"Acta Auditoría - {self.plan.programacion.cotizacion.numero_servicio}"

    def save(self, *args, **kwargs):
        # Automatiza la asignación de fecha_inicio a la fecha de etapa 1 de la programación
        if self.plan and self.plan.programacion and self.plan.programacion.fecha_programacion_etapa1:
            self.fecha_inicio = self.plan.programacion.fecha_programacion_etapa1
        super().save(*args, **kwargs)

class AsistenteActa(models.Model):
    acta = models.ForeignKey(ActaAuditoria, on_delete=models.CASCADE, related_name='asistentes')
    nombre = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)
    firma_apertura = models.ImageField(upload_to='documentacion/firmas/', null=True, blank=True)
    firma_cierre = models.ImageField(upload_to='documentacion/firmas/', null=True, blank=True)

class ActividadCEA(models.Model):
    nivel = models.ForeignKey(NivelAuditoriaCEA, on_delete=models.CASCADE)
    descripcion = models.TextField("Proceso/Actividad/Requisito por Auditar")
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nivel} - {self.descripcion[:30]}"

class HoraActividadPlan(models.Model):
    plan = models.ForeignKey(PlanAuditoria, on_delete=models.CASCADE, related_name='horas_actividades')
    actividad = models.ForeignKey(ActividadCEA, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    # NUEVOS CAMPOS AGREGADOS:
    nombre_auditado = models.CharField(max_length=255, blank=True, null=True, help_text="Nombre de la persona entrevistada")
    cargo_auditado = models.CharField(max_length=100, blank=True, null=True, help_text="Cargo del entrevistado")

    class Meta:
        ordering = ['fecha', 'hora']
        verbose_name = "Actividad del Plan"
        verbose_name_plural = "Actividades del Plan"

    def __str__(self):
        return f"{self.actividad.descripcion[:30]} - {self.fecha} {self.hora}"

class VehiculoInstructor(models.Model):
    archivo_vehiculos_instructores = models.FileField(upload_to='vehiculos_instructores/')

    def __str__(self):
        return f"Archivo: {self.archivo_vehiculos_instructores.name}"
