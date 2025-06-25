import os
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.loader import render_to_string

from .models import Cliente, Solicitud
from .forms import ClienteForm, SolicitudForm

from weasyprint import HTML

# --- Formulario de solicitud por NIT ---
def solicitud(request):
    if request.method == "POST":
        nit = request.POST.get('nit')
        cliente = Cliente.objects.filter(nit=nit).first()
        if cliente:
            return redirect('ver_cliente', cliente_id=cliente.id)
        else:
            return redirect('crear_cliente', nit=nit)
    return render(request, 'solicitudes/solicitud_form.html')

# --- Enviar nueva solicitud ---
def enviar_solicitud(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            nueva_solicitud = form.save(commit=False)
            nueva_solicitud.cliente = cliente
            nueva_solicitud.fecha_solicitud = date.today()
            nueva_solicitud.estado = 'Pendiente'
            nueva_solicitud.save()
            return redirect('listado_solicitudes')
    else:
        form = SolicitudForm(initial={'fecha_solicitud': date.today()})
    return render(request, 'solicitudes/enviar_solicitud.html', {'form': form, 'cliente': cliente})

# --- Ver datos del cliente ---
def ver_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'solicitudes/ver_cliente.html', {'cliente': cliente})

# --- Crear nuevo cliente ---
def crear_cliente(request, nit=None):
    cliente = Cliente.objects.filter(nit=nit).first() if nit else None
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return redirect('ver_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'solicitudes/crear_cliente.html', {'form': form, 'cliente': cliente})

# --- Editar datos del cliente ---
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

# --- Generar PDF profesional usando HTML y WeasyPrint ---
@login_required
def generar_solicitud_pdf(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Procesa los datos para el template (toda la lógica aquí, no en el template)
    fecha_solicitud_str = cliente.fecha_solicitud.strftime('%d/%m/%Y') if cliente.fecha_solicitud else "No registrada"
    categorias = cliente.categorias_certificar.all()
    categorias_str = ", ".join([c.nombre for c in categorias]) if categorias.exists() else "No especificado"
    if cliente.certificado_conformidad and cliente.nombre_ente_certificador:
        certificacion_ente = f"{cliente.certificado_conformidad} - {cliente.nombre_ente_certificador}"
    elif cliente.certificado_conformidad:
        certificacion_ente = cliente.certificado_conformidad
    else:
        certificacion_ente = "No aplica"

    html_string = render_to_string('solicitudes/solicitud_pdf.html', {
        'cliente': cliente,
        'fecha': date.today().strftime('%Y-%m-%d'),
        'fecha_solicitud_str': fecha_solicitud_str,
        'categorias_str': categorias_str,
        'certificacion_ente': certificacion_ente,
    })
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="solicitud.pdf"'
    return response

# --- Listado y gestión de solicitudes ---
@login_required
def solicitudes_view(request):
    solicitudes = Solicitud.objects.all()
    return render(request, 'programacion/solicitudes_list.html', {'solicitudes': solicitudes})

@login_required
def listado_solicitudes(request):
    if not request.user.has_perm('solicitudes.change_solicitud'):
        return HttpResponse("No tienes permiso para ver esta página", status=403)
    solicitudes = Solicitud.objects.filter(estado='Pendiente')
    if request.method == "POST":
        solicitud_id = request.POST.get('solicitud_id')
        nuevo_estado = request.POST.get('estado')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        if nuevo_estado in ['Aprobada', 'Rechazada', 'Programada']:
            solicitud.estado = nuevo_estado
            solicitud.save()
            return redirect('listado_solicitudes')
    return render(request, 'programacion/listado.html', {'solicitudes': solicitudes})

@login_required
def solicitudes_pendientes(request):
    solicitudes = Solicitud.objects.filter(estado="Pendiente")
    return render(request, "solicitudes/pendientes.html", {"solicitudes": solicitudes})
