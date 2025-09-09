from django.urls import path
from . import views

urlpatterns = [
    # --- Solicitudes ---
    path('solicitud/', views.solicitud, name='solicitud'),
    path('enviar_solicitud/<int:cliente_id>/', views.enviar_solicitud, name='enviar_solicitud'),

    # Listado general de solicitudes (todas)
    path('', views.listado_solicitudes, name='listado_solicitudes'),

    # Acciones sobre solicitudes
    path("solicitudes/<int:solicitud_id>/eliminar/", views.eliminar_solicitud, name="eliminar_solicitud"),
    path("solicitudes/<int:solicitud_id>/imprimir/", views.imprimir_solicitud, name="imprimir_solicitud"),

    # --- Clientes ---
    path('clientes/ver/<int:cliente_id>/', views.ver_cliente, name='ver_cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/crear/<str:nit>/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/pdf/', views.generar_solicitud_pdf, name='generar_solicitud_pdf'),

    # --- Solicitudes pendientes para cotización ---
    path('pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
]
