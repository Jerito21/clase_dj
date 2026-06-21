# website/urls.py
"""
Definición de rutas (URLs) de la aplicación 'website'.
Mapea los endpoints HTTP del navegador con las vistas controladoras correspondientes.
Incluye rutas públicas de autenticación, CRUD de productos para operadores y administradores,
exportaciones a múltiples formatos y administración de usuarios.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Rutas de autenticación y acceso principal
    path('',                          views.home,            name='home'),
    path('login/',                    views.login_user,      name='login'),
    path('logout/',                   views.logout_user,     name='logout'),
    path('register/',                 views.register_user,   name='register'),

    # CRUD de productos (operaciones protegidas por roles)
    path('add_product/',              views.add_product,     name='add_product'),
    path('delete_product/<int:pk>/',  views.delete_product,  name='delete_product'),
    path('edit_product/<int:pk>/',    views.edit_product,    name='edit_product'),

    # Reportes y Exportaciones de Datos
    path('reportes/',                 views.reportes,        name='reportes'),
    path('export_csv/',               views.export_csv,      name='export_csv'),
    path('export_pdf/',               views.export_pdf,      name='export_pdf'),

    # Panel de administración e interacción de roles
    path('admin-dashboard/',          views.admin_dashboard, name='admin_dashboard'),
    path('promote-user/<int:pk>/',    views.promote_user,    name='promote_user'),
]