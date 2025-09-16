from django.db import models
from documentacion_auditores.models import ActaAuditoria

class RequisitoAuditoria(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    checkpoint_iaf_md4 = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class EjecucionRequisito(models.Model):
    acta = models.ForeignKey(
        ActaAuditoria,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    # Si requisito puede faltar temporalmente, usa SET_NULL; si siempre es obligatorio, deja CASCADE sin null.
    requisito = models.ForeignKey(
        RequisitoAuditoria,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    cumple = models.BooleanField(default=False)
    no_cumple = models.BooleanField(default=False)
    no_aplica = models.BooleanField(default=False)
    aspecto_mejora = models.BooleanField(default=False)

    concepto_mejora = models.TextField(blank=True, null=True)
    concepto_no_conformidad = models.TextField(blank=True, null=True)

    evidencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="documental",  # tempor

        choices=[
            ("documental", "Evidencia Documental"),
            ("fotografica", "Evidencia Fotográfica"),
            ("audiovisual", "Evidencia Audiovisual"),
            ("documental_fotografica", "Evidencia Documental y Fotográfica"),
            ("documental_audiovisual", "Evidencia Documental y Audiovisual"),
            ("fotografica_audiovisual", "Evidencia Fotográfica y Audiovisual"),
            ("documental_fotografica_audiovisual", "Evidencia Documental, Fotográfica y Audiovisual"),
        ]
    )
    concepto_evidencia = models.TextField(blank=True, null=True)

    imagen1 = models.ImageField(upload_to='evidencias/', blank=True, null=True)
    imagen2 = models.ImageField(upload_to='evidencias/', blank=True, null=True)

    subsanado = models.BooleanField(default=False)
    como_se_subsano = models.TextField(
        blank=True,
        null=True,
        verbose_name="¿Cómo se subsanó la no conformidad?"
    )

    def __str__(self):
        acta_txt = str(self.acta) if self.acta else "Sin acta"
        req_txt = str(self.requisito) if self.requisito else "Sin requisito"
        return f"{acta_txt} - {req_txt}"

class NoConformidad(models.Model):
    ejecucion = models.OneToOneField(EjecucionRequisito, on_delete=models.CASCADE)
    subsanado = models.BooleanField(default=False)
    comentario_subsanacion = models.TextField(blank=True, null=True)
    fecha_subsanacion = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"No conformidad en: {self.ejecucion}"
