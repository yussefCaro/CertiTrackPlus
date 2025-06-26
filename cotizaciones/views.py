from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from solicitudes.models import Solicitud
from .models import Cotizacion, TipoServicio
from .forms import CotizacionForm
from decimal import Decimal
from django.utils.formats import localize


@login_required
def listado_solicitudes(request):
    """ Muestra las solicitudes pendientes para cotización """
    solicitudes = Solicitud.objects.filter(estado="Pendiente").select_related("cliente")  # Optimización con select_related
    return render(request, "cotizaciones/listado_solicitudes.html", {"solicitudes": solicitudes})


@login_required
def crear_cotizacion(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if request.method == "POST":
        print("POST DATA:", request.POST)  # Depuración para ver qué datos llegan
        form = CotizacionForm(request.POST)

        if form.is_valid():
            cotizacion = form.save(commit=False)  # Se guarda la cotización SIN el ManyToMany aún
            cotizacion.solicitud = solicitud
            cotizacion.save()  # Guardamos la cotización en la BD primero

            form.save_m2m()  # Ahora guardamos la relación ManyToMany

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
    cliente = solicitud.cliente  # Cliente asociado a la solicitud

    context = {
        "cotizacion": cotizacion,
        "solicitud": solicitud,
        "cliente": cliente,  # Agregar cliente al contexto
    }

    return render(request, "cotizaciones/detalle_cotizacion.html", context)

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
            cotizacion = form.save(commit=False)  # Guardamos sin ManyToMany
            cotizacion.save()  # Guardamos la cotización primero
            form.save_m2m()  # Ahora guardamos las relaciones ManyToMany

            print("Servicios seleccionados:", form.cleaned_data.get("tipo_servicio"))  # ✅ Solo se ejecuta si el formulario es válido

            return redirect("listado_cotizaciones")

    else:
        form = CotizacionForm(instance=cotizacion)

    return render(request, "cotizaciones/editar_cotizacion.html", {"form": form, "cotizacion": cotizacion})



