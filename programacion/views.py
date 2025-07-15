from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages

from cotizaciones.models import Cotizacion
from .forms import ProgramacionAuditoriaForm, FechaEtapa2Form, FechaEtapa2FormSet
from .models import ProgramacionAuditoria, Auditor, FechaEtapa2, NivelAuditoriaCEA
from django.forms import inlineformset_factory
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

# Días de auditoría por nivel
DIAS_AUDITORIA = {
    "Nivel 1": {"etapa_1": 0.5, "etapa_2": 1},
    "Nivel 2": {"etapa_1": 0.5, "etapa_2": 1.5},
    "Nivel 3": {"etapa_1": 0.5, "etapa_2": 2},
    "Nivel 3 con Formación de Instructores": {"etapa_1": 0.5, "etapa_2": 2.5},
}

@login_required
def listado_cotizaciones(request):
    cotizaciones = Cotizacion.objects.filter(
        estado="Aprobada"
    ).exclude(
        programacionauditoria__estado__in=["En Curso", "Finalizada", "Cancelada"]
    )
    usuarios = User.objects.all()

    if request.method == "POST":
        cotizacion_id = request.POST.get("cotizacion_id")
        cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
        auditor_id = request.POST.get("auditor")
        auditor = get_object_or_404(User, id=auditor_id)

        programacion, _ = ProgramacionAuditoria.objects.get_or_create(cotizacion=cotizacion)
        programacion.fecha_etapa_1 = request.POST.get("fecha_etapa_1")
        programacion.hora_etapa_1 = request.POST.get("hora_etapa_1")
        programacion.fecha_etapa_2 = request.POST.get("fecha_etapa_2")
        programacion.hora_etapa_2 = request.POST.get("hora_etapa_2")
        programacion.auditor = auditor
        programacion.save()

        cotizacion.estado = "Programada"
        cotizacion.save()

        return redirect("listado_cotizaciones")

    return render(request, "programacion/listado.html", {"cotizaciones": cotizaciones, "usuarios": usuarios})

@login_required
def cambiar_estado(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        if nuevo_estado in ["Pendiente", "Aprobada", "Rechazada", "Programada"]:
            cotizacion.estado = nuevo_estado
            cotizacion.save()
    return redirect("listado_cotizaciones")

@login_required
def listado_programaciones(request):
    grupos_usuario = request.user.groups.values_list("name", flat=True)

    if "Auditores" in grupos_usuario:
        try:
            auditor = Auditor.objects.get(user=request.user)
            programaciones = ProgramacionAuditoria.objects.filter(auditores=auditor)
            es_auditor = True
        except Auditor.DoesNotExist:
            programaciones = ProgramacionAuditoria.objects.none()
            es_auditor = True
    else:
        programaciones = ProgramacionAuditoria.objects.select_related("cotizacion__solicitud__cliente").all()
        es_auditor = False

    nivel = request.GET.get('nivel')
    auditor_id = request.GET.get('auditor')
    estado = request.GET.get('estado')

    if nivel:
        programaciones = programaciones.filter(cotizacion__solicitud__cliente__nivel_cea=nivel)
    if auditor_id:
        programaciones = programaciones.filter(auditores__id=auditor_id)
    if estado:
        programaciones = programaciones.filter(estado=estado)

    niveles = ProgramacionAuditoria.objects.values_list('cotizacion__solicitud__cliente__nivel_cea', flat=True).distinct()
    auditores = Auditor.objects.all()
    estados = ProgramacionAuditoria.objects.values_list('estado', flat=True).distinct()

    paginator = Paginator(programaciones, 10)
    page = request.GET.get('page')
    try:
        programaciones_page = paginator.page(page)
    except PageNotAnInteger:
        programaciones_page = paginator.page(1)
    except EmptyPage:
        programaciones_page = paginator.page(paginator.num_pages)

    contexto = {
        "programaciones": programaciones_page,
        "paginator": paginator,
        "page_obj": programaciones_page,
        "is_paginated": programaciones_page.has_other_pages(),
        "pertenece_comercial": "Comercial" in grupos_usuario,
        "pertenece_programacion": "Programación" in grupos_usuario,
        "es_auditor": es_auditor,
        "niveles": niveles,
        "auditores": auditores,
        "estados": estados,
        "nivel_selected": nivel,
        "auditor_selected": auditor_id,
        "estado_selected": estado,
    }
    return render(request, "programacion/listado_programaciones.html", contexto)

@login_required
def imprimir_programacion(request, programacion_id):
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)
    fechas_etapa2 = FechaEtapa2.objects.filter(programacion=programacion)
    usuario = request.user

    context = {
        "programacion": programacion,
        "fechas_etapa2": fechas_etapa2,
        "fecha_hoy": datetime.now().strftime("%d/%m/%Y"),
        "programador_nombre": usuario.get_full_name() or usuario.username,
    }

    html = render_to_string("programacion/imprimir.html", context)
    pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="programacion.pdf"'
    return response

@login_required
def programar_auditoria(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    programacion = ProgramacionAuditoria.objects.filter(cotizacion=cotizacion).first()

    if not programacion:
        if cotizacion.programacionauditoria_set.filter(
            estado__in=["En Curso", "Finalizada", "Cancelada"]
        ).exists():
            messages.error(
                request,
                "Esta cotización ya tiene una programación activa. "
                "Si deseas modificarla, hazlo desde el listado de programaciones."
            )
            return redirect('listado_cotizaciones')
        programacion = ProgramacionAuditoria(cotizacion=cotizacion)

    FechaEtapa2FormSet = inlineformset_factory(
        ProgramacionAuditoria, FechaEtapa2,
        form=FechaEtapa2Form, extra=0, max_num=3, can_delete=True
    )

    if request.method == 'POST':
        form = ProgramacionAuditoriaForm(request.POST, instance=programacion)
        fecha_formset = FechaEtapa2FormSet(request.POST, instance=programacion)

        if form.is_valid() and fecha_formset.is_valid():
            programacion = form.save(commit=False)
            programacion.cotizacion = cotizacion

            # Busca la instancia de NivelAuditoriaCEA por el campo correcto
            try:
                nivel_nombre = cotizacion.solicitud.cliente.nivel_cea
                nivel_obj = NivelAuditoriaCEA.objects.get(nivel=nivel_nombre)
            except (AttributeError, NivelAuditoriaCEA.DoesNotExist):
                nivel_obj = None
            programacion.nivel_auditoria = nivel_obj

            programacion.save()
            fecha_formset.instance = programacion
            fecha_formset.save()
            messages.success(request, 'Programación guardada correctamente.')
            return redirect('listado_programaciones')

    else:
        try:
            nivel_nombre = cotizacion.solicitud.cliente.nivel_cea
            nivel_obj = NivelAuditoriaCEA.objects.get(nivel=nivel_nombre)
        except (AttributeError, NivelAuditoriaCEA.DoesNotExist):
            nivel_obj = None

        form = ProgramacionAuditoriaForm(
            instance=programacion,
            initial={'nivel_auditoria': nivel_obj}
        )
        form.fields['nivel_auditoria'].disabled = True
        fecha_formset = FechaEtapa2FormSet(instance=programacion)

    return render(request, 'programacion/form_programacion.html', {
        'form': form,
        'fecha_formset': fecha_formset,
        'cotizacion': cotizacion,
        'titulo': 'Programar Auditoría',
        'boton_texto': 'Guardar Programación'
    })

@login_required
def eliminar_programacion(request, programacion_id):
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)
    programacion.delete()
    return redirect('listado_programaciones')
