from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from cotizaciones.models import Cotizacion
from .forms import ProgramacionAuditoriaForm, FechaEtapa2Form, FechaEtapa2FormSet
from .models import ProgramacionAuditoria, Auditor, FechaEtapa2
from django.forms import inlineformset_factory
from django.contrib import messages
from weasyprint import HTML  # Usamos WeasyPrint para PDF

# Días de auditoría por nivel
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
    programaciones = ProgramacionAuditoria.objects.select_related("cotizacion__solicitud__cliente").all()
    grupos_usuario = request.user.groups.values_list("name", flat=True)
    contexto = {
        "programaciones": programaciones,
        "pertenece_comercial": "Comercial" in grupos_usuario,
        "pertenece_programacion": "Programación" in grupos_usuario,
    }
    return render(request, "programacion/listado_programaciones.html", contexto)

@login_required
def imprimir_programacion(request, programacion_id):
    """Genera un PDF con la programación de auditoría usando WeasyPrint (compatible con Render)."""
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)
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

    FechaEtapa2FormSet = inlineformset_factory(
        ProgramacionAuditoria,
        FechaEtapa2,
        form=FechaEtapa2Form,
        extra=1,  # Siempre muestra al menos un formulario vacío
        max_num=3,
        can_delete=True
    )

    if request.method == 'POST':
        form = ProgramacionAuditoriaForm(request.POST, instance=programacion)
        fecha_formset = FechaEtapa2FormSet(request.POST, instance=programacion)

        if form.is_valid() and fecha_formset.is_valid():
            programacion = form.save(commit=False)
            programacion.cotizacion = cotizacion
            programacion.save()
            fecha_formset.instance = programacion
            fecha_formset.save()
            messages.success(request, 'Programación guardada correctamente.')
            return redirect('listado_programaciones')
        else:
            messages.error(request, 'Verifica los campos del formulario.')

    else:
        form = ProgramacionAuditoriaForm(instance=programacion)
        fecha_formset = FechaEtapa2FormSet(instance=programacion)

    return render(request, 'programacion/form_programacion.html', {
        'form': form,
        'fecha_formset': fecha_formset,
        'cotizacion': cotizacion,
        'titulo': 'Programar Auditoría',
        'boton_texto': 'Guardar Programación'
    })
