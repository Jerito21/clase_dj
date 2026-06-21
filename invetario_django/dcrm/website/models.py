from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    """
    Modelo principal del sistema de inventario.
    Cada producto pertenece a un usuario (propietario) mediante ForeignKey.
    Implementa el patrón Repository a través del ORM de Django.
    """
    name      = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    category  = models.CharField(max_length=100, verbose_name="Categoría")
    quantity  = models.IntegerField(default=0, verbose_name="Cantidad")
    description = models.TextField(
        blank=True, null=True,
        verbose_name="Descripción",
        help_text="Descripción opcional del producto"
    )
    user      = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Usuario Registrador"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} ({self.quantity} uds.) — {self.category}"
