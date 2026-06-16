from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.home,            name='home'),
    path('login/',                    views.login_user,      name='login'),
    path('logout/',                   views.logout_user,     name='logout'),
    path('register/',                 views.register_user,   name='register'),
    # ── CRUD productos ──────────────────────────────────────────────────────
    path('add_product/',              views.add_product,     name='add_product'),
    path('delete_product/<int:pk>/',  views.delete_product,  name='delete_product'),
    path('edit_product/<int:pk>/',    views.edit_product,    name='edit_product'),
    # ── Reportes & Exportaciones ────────────────────────────────────────────
    path('reportes/',                 views.reportes,        name='reportes'),
    path('export_csv/',               views.export_csv,      name='export_csv'),
    path('export_pdf/',               views.export_pdf,      name='export_pdf'),
    # ── Dashboard Admin ─────────────────────────────────────────────────────
    path('admin-dashboard/',          views.admin_dashboard, name='admin_dashboard'),
    path('promote-user/<int:pk>/',    views.promote_user,    name='promote_user'),
]