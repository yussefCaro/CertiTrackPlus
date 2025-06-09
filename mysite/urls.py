from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Personalización del admin
admin.site.site_title = "CertiTrackPlus Admin"
admin.site.site_header = "CertiTrackPlus Administración"
admin.site.index_title = "Panel de administración"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('tasksapp/', include('tasksapp.urls')),
    path('clientes/', include('solicitudes.urls')),
    path('programacion/', include('programacion.urls')),
    path("cotizaciones/", include("cotizaciones.urls")),
    path('auditores/', include('documentacion_auditores.urls')),
    path('ejecucion/', include('ejecucion_auditoria.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)