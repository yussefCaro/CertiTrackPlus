from django.urls import path
from .views import listado_solicitudes, crear_cotizacion, listado_cotizaciones, detalle_cotizacion, editar_cotizacion
from . import views
urlpatterns = [
    path("solicitudes/", listado_solicitudes, name="listado_solicitudes"),
    path('crear/<int:solicitud_id>/', crear_cotizacion, name='crear_cotizacion'),
    path("cotizaciones/", listado_cotizaciones, name="listado_cotizaciones"),
    path("detalle/<int:cotizacion_id>/", detalle_cotizacion, name="detalle_cotizacion"),
    path("editar/<int:cotizacion_id>/", editar_cotizacion, name="editar_cotizacion"),
    path('cotizacion/<int:cotizacion_id>/pdf/', views.cotizacion_pdf, name='cotizacion_pdf'),


]
