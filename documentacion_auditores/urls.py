from django.urls import path
from . import views
from .views import editar_plan

urlpatterns = [
    path('dashboard/', views.dashboard_auditor, name='dashboard_auditor'),
    path('plan/<int:programacion_id>/', views.crear_plan, name='crear_plan'),
    path('plan/<int:plan_id>/imprimir/', views.imprimir_plan, name='imprimir_plan'),
    path('acta/<int:acta_id>/imprimir/', views.imprimir_acta, name='imprimir_acta'),
    path('auditores/plan/editar/<int:plan_id>/', editar_plan, name='editar_plan'),
    path('acta/<int:programacion_id>/pdf/', views.generar_acta_pdf, name='generar_acta_pdf'),
    path('acta/<int:acta_id>/asistente/agregar/', views.agregar_asistentes, name='agregar_asistentes'),
    path('acta/<int:acta_id>/asistentes/', views.asistentes_acta_view, name='asistentes_acta'),
    path('plan/<int:plan_id>/aprobar/', views.aprobar_plan_cliente, name='aprobar_plan_cliente'),
    path('programacion/mis/', views.listado_programaciones_auditor, name='listado_programaciones_auditor'),







]