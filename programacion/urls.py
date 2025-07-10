from django.urls import path
from . import views  # Importamos las vistas correctamente

urlpatterns = [
    path('cotizaciones/', views.listado_cotizaciones, name='listado_cotizaciones'),  # Se cambia a listado_cotizaciones
    path('cotizacion/<int:cotizacion_id>/cambiar_estado/', views.cambiar_estado, name='cambiar_estado'),
    path("programaciones/", views.listado_programaciones, name="listado_programaciones"),
    path("imprimir/<int:programacion_id>/", views.imprimir_programacion, name="imprimir_programacion"),
    path('programar_auditoria/<int:cotizacion_id>/', views.programar_auditoria, name='programar_auditoria'),
    path('programacion/programar/<int:cotizacion_id>/', views.programar_auditoria, name='programar_auditoria'),
    path('programacion/eliminar/<int:programacion_id>/', views.eliminar_programacion, name='eliminar_programacion'),

]
