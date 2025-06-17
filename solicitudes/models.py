from django.db import models
from datetime import date

# Definimos las categorías de certificación como choices
class CategoriaChoices(models.TextChoices):
    A1 = "A1", "A1"
    A2 = "A2", "A2"
    B1 = "B1", "B1"
    B2 = "B2", "B2"
    B3 = "B3", "B3"
    C1 = "C1", "C1"
    C2 = "C2", "C2"
    C3 = "C3", "C3"
    FORMACION_A1 = "FORMACION DE INSTRUCTORES A1", "FORMACION DE INSTRUCTORES A1"
    FORMACION_A2 = "FORMACION DE INSTRUCTORES A2", "FORMACION DE INSTRUCTORES A2"
    FORMACION_B1 = "FORMACION DE INSTRUCTORES B1", "FORMACION DE INSTRUCTORES B1"
    FORMACION_B2 = "FORMACION DE INSTRUCTORES B2", "FORMACION DE INSTRUCTORES B2"
    FORMACION_B3 = "FORMACION DE INSTRUCTORES B3", "FORMACION DE INSTRUCTORES B3"
    FORMACION_C1 = "FORMACION DE INSTRUCTORES C1", "FORMACION DE INSTRUCTORES C1"
    FORMACION_C2 = "FORMACION DE INSTRUCTORES C2", "FORMACION DE INSTRUCTORES C2"
    FORMACION_C3 = "FORMACION DE INSTRUCTORES C3", "FORMACION DE INSTRUCTORES C3"

NIVELES_CEA = [
    ("Nivel 1", "Nivel 1"),
    ("Nivel 2", "Nivel 2"),
    ("Nivel 3", "Nivel 3"),
    ("Nivel 3 con Formación de Instructores", "Nivel 3 con Formación de Instructores"),
]

CERTIFICADO_CONFORMIDAD_CHOICES = [
    ("Si", "Sí"),
    ("No", "No aplica"),
]

class Categoria(models.Model):
    nombre = models.CharField(max_length=40, unique=True, choices=CategoriaChoices.choices)

    def __str__(self):
        return self.get_nombre_display()  # ✅ Ahora sí funcionará correctamente

class Cliente(models.Model):
    nit = models.CharField(max_length=20, unique=True)  # Nit único
    nombre_propietario = models.CharField(max_length=100)
    nombre_establecimiento = models.CharField(max_length=100)
    representante_legal = models.CharField(max_length=100)
    cedula_ciudadania = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    representante_organismo = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    telefono_fijo = models.CharField(max_length=20, blank=True, null=True)
    telefono_celular = models.CharField(max_length=20)
    correo_electronico = models.EmailField()
    nivel_cea = models.CharField(max_length=50, choices=NIVELES_CEA)
    cantidad_vehiculos = models.IntegerField(null=True, blank=True)
    cantidad_instructores = models.IntegerField(null=True, blank=True)
    categorias_certificar = models.ManyToManyField(Categoria, blank=True)
    certificado_conformidad = models.CharField(max_length=2, choices=CERTIFICADO_CONFORMIDAD_CHOICES, default="No")
    nombre_ente_certificador = models.CharField(max_length=100, blank=True, null=True)  # Se llena si es "Sí"
    fecha_solicitud = models.DateField(null=True, blank=True)  # Se establece solo cuando se envía la solicitud
    observaciones = models.TextField(blank=True, null=True)

    def enviar_solicitud(self):
        """Método para establecer la fecha de solicitud al momento de enviar la solicitud."""
        if not self.fecha_solicitud:
            self.fecha_solicitud = date.today()
            self.save()

    def __str__(self):
        return self.nombre_establecimiento

# Modelo Solicitud
class Solicitud(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="solicitudes_solicitudes")  # Relación con el modelo Cliente
    fecha_solicitud = models.DateField(default=date.today)  # Fecha en que se crea la solicitud
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada')
        ],
        default='Pendiente'
    )  # Estado de la solicitud

    def __str__(self):
        return f"Solicitud para {self.cliente.nombre_establecimiento} - {self.estado}"
