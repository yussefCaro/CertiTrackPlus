from django.urls import path
from . import views
from .views import solicitudes_pendientes

urlpatterns = [
    path('solicitud/', views.solicitud, name='solicitud'),
    path('clientes/ver/<int:cliente_id>/', views.ver_cliente, name='ver_cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/crear/<str:nit>/', views.crear_cliente, name='crear_cliente'),
    path('clientes/solicitud/pdf/<int:cliente_id>/', views.generar_solicitud_pdf, name='generar_solicitud_pdf'),
    path('enviar_solicitud/<int:cliente_id>/', views.enviar_solicitud, name='enviar_solicitud'),
    path("pendientes/", solicitudes_pendientes, name="solicitudes_pendientes"),
    path('solicitud/<int:cliente_id>/pdf/', views.generar_solicitud_pdf, name='generar_solicitud_pdf'),

]
