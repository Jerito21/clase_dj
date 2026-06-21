"""
Configuración de URLs del proyecto principal DCRM.
Define los puntos de entrada principales del sitio: el panel administrativo global de Django
y las rutas modulares de la aplicación 'website'.
"""
from django.contrib import admin
from django.urls import path, include

# Personalización del sitio de administración de Django
admin.site.site_header = "Administración del Sistema de Inventario DCRM"
admin.site.site_title = "DCRM Admin"
admin.site.index_title = "Gestión de Módulos del Sistema"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
]
