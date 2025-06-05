from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from weasyprint import HTML
from cotizaciones.models import Cotizacion
from .forms import ProgramacionAuditoriaForm, FechaEtapa2Form, FechaEtapa2FormSet
from .models import ProgramacionAuditoria, Auditor, FechaEtapa2
from django.forms import modelformset_factory
from django.contrib import messages




# Definimos los días de auditoría por nivel
DIAS_AUDITORIA = {
    "Nivel 1": {"etapa_1": 0.5, "etapa_2": 1},
    "Nivel 2": {"etapa_1": 0.5, "etapa_2": 1.5},
    "Nivel 3": {"etapa_1": 0.5, "etapa_2": 2},
    "Nivel 3 con Formación de Instructores": {"etapa_1": 0.5, "etapa_2": 2.5},
}

@login_required
def listado_cotizaciones(request):
    cotizaciones = Cotizacion.objects.filter(estado="Pendiente")
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
    """ Muestra la lista de programaciones de auditoría. """
    programaciones = ProgramacionAuditoria.objects.select_related("cotizacion__solicitud__cliente").all()



    # Obtener los grupos del usuario
    grupos_usuario = request.user.groups.values_list("name", flat=True)

    contexto = {
        "programaciones": programaciones,
        "pertenece_comercial": "Comercial" in grupos_usuario,
        "pertenece_programacion": "Programación" in grupos_usuario,  # Asegúrate de que el nombre del grupo es correcto
    }

    return render(request, "programacion/listado_programaciones.html", contexto)



@login_required
def imprimir_programacion(request, programacion_id):
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)
    tipos_servicio = programacion.cotizacion.tipo_servicio.all()
    print("Tipos de servicio:", list(tipos_servicio))
    fechas_etapa2 = FechaEtapa2.objects.filter(programacion=programacion)
    html = render_to_string(
        "programacion/imprimir.html",
        {
            "programacion": programacion,
            "fechas_etapa2": fechas_etapa2,
        },
    )
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="programacion.pdf"'
    return response



@login_required
def programar_auditoria(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    programacion, _ = ProgramacionAuditoria.objects.get_or_create(cotizacion=cotizacion)

    FechaEtapa2FormSet = modelformset_factory(FechaEtapa2, form=FechaEtapa2Form, extra=1, max_num=3, can_delete=True)

    if request.method == 'POST':
        form = ProgramacionAuditoriaForm(request.POST, instance=programacion)
        fecha_formset = FechaEtapa2FormSet(request.POST, queryset=FechaEtapa2.objects.filter(programacion=programacion))

        if form.is_valid() and fecha_formset.is_valid():
            nivel_auditoria = form.cleaned_data.get('nivel_auditoria')
            if not nivel_auditoria:
                messages.error(request, 'Debe seleccionar un nivel de auditoría.')
            elif nivel_auditoria == 'Nivel 3 con Formación de Instructores' and fecha_formset.total_form_count() > 3:
                messages.error(request, 'No se pueden agregar más de 3 fechas para este nivel.')
            else:
                programacion = form.save()
                for fecha in fecha_formset.save(commit=False):
                    fecha.programacion = programacion
                    fecha.save()
                for fecha in fecha_formset.deleted_objects:
                    fecha.delete()

                messages.success(request, 'Programación guardada correctamente.')
                return redirect('listado_programaciones')
    else:
        form = ProgramacionAuditoriaForm(instance=programacion)
        fecha_formset = FechaEtapa2FormSet(queryset=FechaEtapa2.objects.filter(programacion=programacion))

    return render(request, 'programacion/form_programacion.html', {
        'form': form,
        'fecha_formset': fecha_formset,
        'cotizacion': cotizacion,
        'titulo': 'Programar Auditoría',
        'boton_texto': 'Guardar Programación'
    })
