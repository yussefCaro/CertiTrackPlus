from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import PlanAuditoria, ActaAuditoria, AsistenteActa, ActividadCEA, HoraActividadPlan
from .forms import PlanAuditoriaForm, ActaAuditoriaForm, AsistenteActaForm, HoraActividadPlanFormSet
from programacion.models import ProgramacionAuditoria, Auditor
from datetime import timedelta
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import os


# 🔐 Validación de grupo
def auditor_check(user):
    return user.groups.filter(name='Auditores').exists()

@login_required
def listado_programaciones_auditor(request):
    try:
        auditor = Auditor.objects.get(user=request.user)
        programaciones = ProgramacionAuditoria.objects.filter(auditores=auditor)
    except Auditor.DoesNotExist:
        programaciones = ProgramacionAuditoria.objects.none()

    return render(request, "programacion/listado_programaciones.html", {
        "programaciones": programaciones,
        "es_auditor": True,
    })

@login_required
@user_passes_test(auditor_check)
def dashboard_auditor(request):
    auditor = Auditor.objects.get(user=request.user)
    programaciones = ProgramacionAuditoria.objects.filter(
        auditores=auditor
    ).exclude(planauditoria__aprobado_por_cliente=True)
    planes = PlanAuditoria.objects.filter(auditor=request.user)

    return render(request, 'documentacion_auditores/dashboard.html', {
        'programaciones': programaciones,
        'planes': planes,
    })


@login_required
@user_passes_test(auditor_check)
def crear_plan(request, programacion_id):
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)

    plan_existente = PlanAuditoria.objects.filter(programacion=programacion).first()
    if plan_existente:
        messages.info(request, "Ya existe un plan para esta programación. Puedes editarlo aquí.")
        return redirect('editar_plan', plan_existente.id)

    actividades = list(ActividadCEA.objects.filter(nivel=programacion.nivel_auditoria))
    fechas_disponibles = [f.fecha for f in programacion.fechas_etapa2.all()]

    # ← CAMBIO: Usar el FormSet actualizado con los nuevos campos
    formset_factory = modelformset_factory(
        HoraActividadPlan,
        fields=('fecha', 'hora', 'nombre_auditado', 'cargo_auditado'),  # ← NUEVOS CAMPOS
        extra=len(actividades)
    )

    if request.method == 'POST':
        form = PlanAuditoriaForm(request.POST, request.FILES)
        formset = formset_factory(request.POST)

        if form.is_valid() and formset.is_valid():
            plan = form.save(commit=False)
            plan.programacion = programacion
            plan.auditor = request.user
            # Tomar la primera fecha de etapa 2 y restarle 2 días
            fecha_etapa2 = programacion.fechas_etapa2.order_by("fecha").first()
            if fecha_etapa2:
                plan.fecha_aprobacion = fecha_etapa2.fecha - timedelta(days=2)
            else:
                plan.fecha_aprobacion = timezone.now().date()

            plan.save()

            ActaAuditoria.objects.get_or_create(plan=plan)

            # ← CAMBIO: Guardar con los nuevos campos
            for subform, actividad in zip(formset, actividades):
                if subform.cleaned_data:  # ← Validar datos
                    hora_actividad = subform.save(commit=False)
                    hora_actividad.plan = plan
                    hora_actividad.actividad = actividad
                    # Los campos nombre_auditado y cargo_auditado ya están incluidos automáticamente
                    hora_actividad.save()

            messages.success(request, "Plan de auditoría creado correctamente.")
            return redirect('dashboard_auditor')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = PlanAuditoriaForm()

        # ← CAMBIO: Crear formset inicial con actividades y campos nuevos
        initial_data = []
        for actividad in actividades:
            initial_data.append({
                'actividad': actividad.id,
                'nombre_auditado': '',  # ← Campo nuevo
                'cargo_auditado': ''  # ← Campo nuevo
            })
        formset = formset_factory(queryset=HoraActividadPlan.objects.none(), initial=initial_data)

    return render(request, 'documentacion_auditores/plan_form.html', {
        'form': form,
        'formset': formset,
        'actividades': actividades,
        'fechas_disponibles': fechas_disponibles,
        'programacion': programacion,
    })


@login_required
@user_passes_test(auditor_check)
def editar_plan(request, plan_id):
    plan = get_object_or_404(PlanAuditoria, id=plan_id)

    if plan.aprobado_por_cliente:
        messages.error(request, "No puede editar un plan ya aprobado por el cliente.")
        return redirect('dashboard_auditor')

    actividades = list(ActividadCEA.objects.filter(nivel=plan.programacion.nivel_auditoria))
    fechas_disponibles = [f.fecha for f in plan.programacion.fechas_etapa2.all()]
    queryset_horas = HoraActividadPlan.objects.filter(plan=plan)

    # ← CAMBIO: FormSet con los nuevos campos
    formset_factory = modelformset_factory(
        HoraActividadPlan,
        fields=('fecha', 'hora', 'nombre_auditado', 'cargo_auditado'),  # ← NUEVOS CAMPOS
        extra=0
    )

    if request.method == 'POST':
        form = PlanAuditoriaForm(request.POST, request.FILES, instance=plan)
        formset = formset_factory(request.POST, queryset=queryset_horas)

        if form.is_valid() and formset.is_valid():
            form.save()
            # ← CAMBIO: Guardar con nuevos campos
            for subform, actividad in zip(formset, actividades):
                if subform.cleaned_data:  # ← Validar datos
                    hora_actividad = subform.save(commit=False)
                    hora_actividad.plan = plan
                    hora_actividad.actividad = actividad
                    # Los campos nombre_auditado y cargo_auditado se guardan automáticamente
                    hora_actividad.save()
            return redirect('dashboard_auditor')
    else:
        form = PlanAuditoriaForm(instance=plan)
        formset = formset_factory(queryset=queryset_horas)

    return render(request, 'documentacion_auditores/plan_form.html', {
        'form': form,
        'formset': formset,
        'actividades': actividades,
        'fechas_disponibles': fechas_disponibles,
        'programacion': plan.programacion,
        'editando': True,
    })

@login_required
@user_passes_test(auditor_check)
def aprobar_plan_cliente(request, plan_id):
    plan = get_object_or_404(PlanAuditoria, id=plan_id)

    if request.method == 'POST':
        plan.aprobado_por_cliente = True

        # Calcular fecha de aprobación cliente: 2 días antes de la primera fecha de etapa 2
        fecha_etapa2 = plan.programacion.fechas_etapa2.order_by("fecha").first()
        if fecha_etapa2:
            plan.fecha_aprobacion_cliente = fecha_etapa2.fecha - timedelta(days=2)
        else:
            plan.fecha_aprobacion_cliente = timezone.now().date()

        plan.save()

        if not hasattr(plan, 'acta'):
            ActaAuditoria.objects.create(
                plan=plan,
                representante_legal_nombre=plan.programacion.cotizacion.solicitud.cliente.representante_legal,
                representante_legal_cargo="Representante Legal",
                fecha_inicio=plan.programacion.fechas_etapa2.first().fecha if plan.programacion.fechas_etapa2.exists() else timezone.now().date(),
                fecha_cierre=plan.programacion.fechas_etapa2.last().fecha if plan.programacion.fechas_etapa2.exists() else timezone.now().date(),
            )

        messages.success(request, "El plan ha sido aprobado por el cliente.")
    return redirect('dashboard_auditor')

@login_required
@user_passes_test(auditor_check)
def imprimir_plan(request, plan_id):
    plan = get_object_or_404(PlanAuditoria, id=plan_id)
    programacion = plan.programacion
    hora_actividades = plan.horas_actividades.all().order_by('fecha', 'hora')
    logo_path = os.path.join(settings.STATIC_ROOT, 'myapp', 'AQ_color.png')

    html_string = render_to_string(
        'documentacion_auditores/plan_pdf.html',
        {
            'plan': plan,
            'programacion': programacion,
            'hora_actividades': hora_actividades,
            'logo_path': logo_path,
        }
    )
    pdf_file = HTML(string=html_string).write_pdf()
    return HttpResponse(pdf_file, content_type='application/pdf')

@login_required
@user_passes_test(auditor_check)
def imprimir_acta(request, acta_id):
    acta = get_object_or_404(ActaAuditoria, id=acta_id)
    logo_path = os.path.join(settings.STATIC_ROOT, 'myapp', 'AQ_color.png')

    html_string = render_to_string(
        'documentacion_auditores/acta_pdf.html',
        {
            'acta': acta,
            'logo_path': logo_path,
        }
    )
    pdf_file = HTML(string=html_string).write_pdf()
    return HttpResponse(pdf_file, content_type='application/pdf')

@login_required
@user_passes_test(auditor_check)
def generar_acta_pdf(request, programacion_id):
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)
    cotizacion = programacion.cotizacion
    cliente = cotizacion.solicitud.cliente
    plan = get_object_or_404(PlanAuditoria, programacion_id=programacion_id)
    acta = plan.acta

    if not acta.asistentes.exists():
        messages.error(request, "Debe registrar al menos un asistente antes de imprimir el acta.")
        return redirect('dashboard_auditor')

    asistentes = acta.asistentes.all()
    fechas = programacion.fechas_etapa2.all()
    logo_path = os.path.join(settings.STATIC_ROOT, 'myapp', 'AQ_color.png')

    context = {
        'programacion': programacion,
        'cotizacion': cotizacion,
        'cliente': cliente,
        'plan': plan,
        'acta': acta,
        'fechas': fechas,
        'asistentes': asistentes,
        'auditor': request.user.get_full_name(),
        'logo_path': logo_path,
    }

    html_string = render_to_string('documentacion_auditores/acta_pdf.html', context)
    pdf_file = HTML(string=html_string).write_pdf()
    return HttpResponse(pdf_file, content_type='application/pdf')

@login_required
def imprimir_programacion(request, programacion_id):
    programacion = get_object_or_404(ProgramacionAuditoria, id=programacion_id)
    logo_path = os.path.join(settings.STATIC_ROOT, 'myapp', 'AQ_color.png')

    html_string = render_to_string('documentacion_auditores/programacion_pdf.html', {
        'programacion': programacion,
        'logo_path': logo_path,
    })
    pdf_file = HTML(string=html_string).write_pdf()
    return HttpResponse(pdf_file, content_type='application/pdf')

@login_required
def agregar_asistentes(request, acta_id):
    acta = get_object_or_404(ActaAuditoria, id=acta_id)
    AsistenteFormSet = inlineformset_factory(ActaAuditoria, AsistenteActa, form=AsistenteActaForm, extra=5, can_delete=True)

    if request.method == 'POST':
        formset = AsistenteFormSet(request.POST, instance=acta)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Asistente(s) guardado(s) correctamente.")
            return redirect('agregar_asistentes', acta_id=acta.id)
    else:
        formset = AsistenteFormSet(instance=acta)

    return render(request, 'documentacion_auditores/agregar_asistentes.html', {
        'formset': formset,
        'acta': acta,
    })

@login_required
def asistentes_acta_view(request, acta_id):
    acta = get_object_or_404(ActaAuditoria, id=acta_id)
    AsistenteFormSet = inlineformset_factory(ActaAuditoria, AsistenteActa, form=AsistenteActaForm, extra=1, can_delete=True)

    if request.method == 'POST':
        formset = AsistenteFormSet(request.POST, instance=acta)
        if formset.is_valid():
            formset.save()
            return redirect('asistentes_acta', acta_id=acta.id)
    else:
        formset = AsistenteFormSet(instance=acta)
        if all([form.instance.pk for form in formset.forms]):
            AsistenteFormSet = inlineformset_factory(ActaAuditoria, AsistenteActa, form=AsistenteActaForm, extra=1, can_delete=True)
            formset = AsistenteFormSet(instance=acta)

    return render(request, 'documentacion_auditores/asistentes_acta_form.html', {
        'formset': formset,
        'acta': acta,
    })
