from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from solicitudes.models import Solicitud
from .models import Cotizacion, TipoServicio
from .forms import CotizacionForm
from decimal import Decimal
from django.utils.formats import localize
from django.template.loader import render_to_string
from weasyprint import HTML
import os
from django.conf import settings


@login_required
def listado_solicitudes(request):
    """ Muestra las solicitudes pendientes para cotización """
    solicitudes = Solicitud.objects.filter(estado="Pendiente").select_related("cliente")
    return render(request, "cotizaciones/listado_solicitudes.html", {"solicitudes": solicitudes})


@login_required
def crear_cotizacion(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if request.method == "POST":
        print("POST DATA:", request.POST)
        form = CotizacionForm(request.POST)

        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.solicitud = solicitud
            cotizacion.save()
            form.save_m2m()

            solicitud.estado = "Cotizada"
            solicitud.save()

            return redirect("listado_cotizaciones")

    else:
        form = CotizacionForm()

    return render(request, "cotizaciones/crear_cotizacion.html", {"form": form, "solicitud": solicitud})


@login_required
def listado_cotizaciones(request):
    """ Muestra la lista de cotizaciones creadas """
    es_comercial = request.user.groups.filter(name='Comercial').exists()
    es_programacion = request.user.groups.filter(name='Programacion').exists()

    if es_programacion:
        cotizaciones = Cotizacion.objects.filter(estado='Aprobada')
    else:
        cotizaciones = Cotizacion.objects.all()

    return render(
        request,
        "cotizaciones/listado_cotizaciones.html",
        {
            "cotizaciones": cotizaciones,
            "es_comercial": es_comercial,
            "es_programacion": es_programacion,
        }
    )


@login_required
def detalle_cotizacion(request, cotizacion_id):
    """ Muestra el detalle de una cotización """
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    cotizacion.precio_neto = localize(cotizacion.precio_neto)
    cotizacion.precio_iva = localize(cotizacion.precio_iva)
    cotizacion.precio_total = localize(cotizacion.precio_total)

    solicitud = cotizacion.solicitud
    cliente = solicitud.cliente

    context = {
        "cotizacion": cotizacion,
        "solicitud": solicitud,
        "cliente": cliente,
    }

    return render(request, "cotizaciones/detalle_cotizacion.html", context)


@login_required
def cotizacion_pdf(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    cliente = cotizacion.solicitud.cliente
    usuario = request.user

    # Categorías
    categorias = cliente.categorias_certificar.all()
    categorias_str = ", ".join([c.nombre for c in categorias]) if categorias.exists() else "No especificado"

    # Certificación de otro ente
    if cliente.certificado_conformidad and cliente.Organismo_certificador_y_alcance:
        certificacion_ente = f"{cliente.certificado_conformidad} - {cliente.Organismo_certificador_y_alcance}"
    elif cliente.certificado_conformidad:
        certificacion_ente = cliente.certificado_conformidad
    else:
        certificacion_ente = "No aplica"

    # Datos de días de auditoría por nivel CEA
    tabla_dias = {
        "Nivel 1": {"etapa1": "0,5 días", "etapa2": "1 día"},
        "Nivel 2": {"etapa1": "0,5 días", "etapa2": "1,5 días"},
        "Nivel 3": {"etapa1": "0,5 días", "etapa2": "2 días"},
        "Nivel 3 con Formación de Instructores": {"etapa1": "0,5 días", "etapa2": "2,5 días"},
    }

    nivel_cliente = getattr(cliente, "nivel_cea", None)
    dias_cliente = tabla_dias.get(nivel_cliente, None)

    # Ruta absoluta al logo
    logo_path = os.path.join(settings.STATIC_ROOT, 'myapp', 'AQ_color.png')

    # Renderizar HTML
    html_string = render_to_string('cotizaciones/cotizacion_pdf.html', {
        'cotizacion': cotizacion,
        'cliente': cliente,
        'categorias_str': categorias_str,
        'certificacion_ente': certificacion_ente,
        'organismo_certificador': cliente.Organismo_certificador_y_alcance,
        'logo_path': logo_path,
        'nivel_cliente': nivel_cliente,
        'dias_cliente': dias_cliente,
        'usuario': usuario,
    })

    pdf_file = HTML(string=html_string, base_url=".").write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero_servicio}.pdf"'
    return response


@login_required
def solicitudes_pendientes(request):
    solicitudes = Solicitud.objects.filter(estado="Pendiente")
    return render(request, "solicitudes/pendientes.html", {"solicitudes": solicitudes})


@login_required
def editar_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    if request.method == "POST":
        form = CotizacionForm(request.POST, instance=cotizacion)

        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.save()
            form.save_m2m()

            print("Servicios seleccionados:", form.cleaned_data.get("tipo_servicio"))

            return redirect("listado_cotizaciones")

    else:
        form = CotizacionForm(instance=cotizacion)

    return render(request, "cotizaciones/editar_cotizacion.html", {"form": form, "cotizacion": cotizacion})
