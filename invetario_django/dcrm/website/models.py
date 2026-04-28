from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    category = models.CharField(max_length=100, verbose_name="Categoría")
    quantity = models.IntegerField(default=0, verbose_name="Cantidad")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name="Usuario Registrador")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    def __str__(self):
        return f"{self.name} ({self.quantity})"
