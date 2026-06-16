from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Administración del modelo Product.
    Permite al superusuario gestionar todos los productos
    con filtros, búsqueda y visualización organizada.
    """
    list_display = ['name', 'category', 'quantity', 'user', 'created_at']
    list_filter = ['category', 'user']
    search_fields = ['name', 'category', 'user__username']
    ordering = ['-created_at']
    list_per_page = 25
    readonly_fields = ['created_at']

    fieldsets = (
        ('Información del Producto', {
            'fields': ('name', 'category', 'quantity', 'user')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
