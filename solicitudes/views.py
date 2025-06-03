import os

from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from .models import Cliente
from .forms import ClienteForm, SolicitudForm
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Solicitud
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch



# Vista para manejar el formulario de solicitud
def solicitud(request):
    if request.method == "POST":
        nit = request.POST.get('nit')
        cliente = Cliente.objects.filter(nit=nit).first()

        if cliente:
            return redirect('ver_cliente', cliente_id=cliente.id)
        else:
            return redirect('crear_cliente', nit=nit)

    return render(request, 'solicitudes/solicitud_form.html')


# Vista para enviar la solicitud con fecha
def enviar_solicitud(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)  # Asegura que el cliente existe

    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            nueva_solicitud = form.save(commit=False)
            nueva_solicitud.cliente = cliente  # Asignar cliente
            nueva_solicitud.fecha_solicitud = date.today()
            nueva_solicitud.estado = 'Pendiente'
            nueva_solicitud.save()
            return redirect('listado_solicitudes')

    else:
        form = SolicitudForm(initial={'fecha_solicitud': date.today()})

    return render(request, 'solicitudes/enviar_solicitud.html', {'form': form, 'cliente': cliente})


# Vista para ver los datos del cliente
def ver_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'solicitudes/ver_cliente.html', {'cliente': cliente})


# Vista para crear un nuevo cliente con el NIT prellenado
def crear_cliente(request, nit=None):
    # Si se proporciona un nit, intentamos obtener un cliente
    cliente = None
    if nit:
        cliente = Cliente.objects.filter(nit=nit).first()

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()  # Guarda el cliente
            return redirect('ver_cliente', cliente_id=cliente.id)  # Redirige a la vista de ver_cliente
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'solicitudes/crear_cliente.html', {'form': form, 'cliente': cliente})


# Vista para editar datos del cliente
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('ver_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'solicitudes/editar_cliente.html', {'form': form, 'cliente': cliente})


# Generación de PDF con datos del cliente




@login_required
def generar_solicitud_pdf(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="solicitud_servicio.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    margen_x = 50

    # --- LOGO Y NIT ---
    # Ruta absoluta al logo (ajusta según tu estructura de carpetas)
    logo_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'myapp', 'AQ_color.png')
    if os.path.exists(logo_path):
        img = ImageReader(logo_path)
        # Tamaño del logo (ajusta según prefieras)
        img_width = 100
        img_height = 40
        # Posición del logo (superior izquierda)
        x_logo = margen_x
        y_logo = height - 65
        pdf.drawImage(img, x_logo, y_logo, width=img_width, height=img_height, mask='auto')
        # NIT debajo del logo
        pdf.setFont("Helvetica", 10)
        pdf.drawString(x_logo, y_logo - 8, "Nit. 900509054-9")
    else:
        print("No se encontró el logo en:", logo_path)

    # TÍTULO

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(200, height - 80, "Solicitud de Auditoría")  # Subir el título
    pdf.line(margen_x, height - 90, width - margen_x, height - 90)  # Subir línea

    # Posición inicial de la tabla más abajo
    y_inicio_tabla = height - 500

    data = [
        ["NIT:", cliente.nit],
        ["Nombre del Propietario:", cliente.nombre_propietario],
        ["Establecimiento Comercial:", cliente.nombre_establecimiento],
        ["Representante Legal:", cliente.representante_legal],
        ["Cédula de Ciudadanía:", cliente.cedula_ciudadania],
        ["Ciudad:", cliente.ciudad],
        ["Departamento:", cliente.departamento],
        ["Dirección:", cliente.direccion],
        ["Representante del Organismo:", cliente.representante_organismo],
        ["Cargo:", cliente.cargo],
        ["Correo Electrónico:", cliente.correo_electronico],
        ["Teléfono Celular:", cliente.telefono_celular],
        ["Nivel del CEA:", cliente.nivel_cea],
        ["Categorías a Certificar:", ", ".join(categoria.nombre for categoria in
                                               cliente.categorias_certificar.all()) if cliente.categorias_certificar.exists() else "No especificado"],
        ["Cantidad de Vehículos:", cliente.cantidad_vehiculos],
        ["Cantidad de Instructores:", cliente.cantidad_instructores],
        ["Certificación de otro ente:", f"{cliente.certificado_conformidad} - {cliente.nombre_ente_certificador}"],
        ["Fecha de Solicitud:", cliente.fecha_solicitud.strftime('%d/%m/%Y') if cliente.fecha_solicitud else "No registrada"],
        ["Observaciones:", cliente.observaciones if cliente.observaciones else "Ninguna"]
    ]

    table = Table(data, colWidths=[200, 300])  # Ajuste de ancho
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, margen_x, y_inicio_tabla)  # Mover la tabla más abajo

    # FIRMA DEL REPRESENTANTE
    pdf.setFont("Helvetica", 12)
    pdf.drawString(margen_x + 50, 100, "_________________________")
    pdf.drawString(margen_x + 50, 80, "Firma del Representante")

    pdf.showPage()
    pdf.save()

    return response






@login_required
def solicitudes_view(request):
    solicitudes = Solicitud.objects.all()
    return render(request, 'programacion/solicitudes_list.html', {'solicitudes': solicitudes})




@login_required

def listado_solicitudes(request):
    # Verificar permisos del usuario en la consola
    print("Permisos del usuario:", request.user.get_all_permissions())

    if not request.user.has_perm('solicitudes.change_solicitud'):
        return HttpResponse("No tienes permiso para ver esta página", status=403)

    solicitudes = Solicitud.objects.filter(estado='Pendiente')  # Solo las Pendientes

    if request.method == "POST":
        # Lógica para cambiar el estado
        solicitud_id = request.POST.get('solicitud_id')
        nuevo_estado = request.POST.get('estado')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)

        # Cambiar el estado solo si está permitido
        if nuevo_estado in ['Aprobada', 'Rechazada', 'Programada']:  # Asegurarse de que el estado sea válido
            solicitud.estado = nuevo_estado
            solicitud.save()
            return redirect('listado_solicitudes')

    return render(request, 'programacion/listado.html', {'solicitudes': solicitudes})




@login_required
def solicitudes_pendientes(request):
    """ Muestra las solicitudes que aún no tienen cotización """
    solicitudes = Solicitud.objects.filter(estado="Pendiente")
    return render(request, "solicitudes/pendientes.html", {"solicitudes": solicitudes})


