from django.test import TestCase
from django.contrib.auth.models import User
from website.models import Product


class ProductModelTest(TestCase):
    """Pruebas unitarias para el modelo de productos (Product)."""

    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            username='operador1',
            email='op1@example.com',
            password='password123'
        )

    def test_product_creation(self):
        """Verifica que un producto se cree correctamente con sus campos asignados."""
        product = Product.objects.create(
            name='Teclado Mecánico',
            category='Periféricos',
            quantity=15,
            description='Teclado RGB con switches mecánicos',
            user=self.user
        )
        self.assertEqual(product.name, 'Teclado Mecánico')
        self.assertEqual(product.category, 'Periféricos')
        self.assertEqual(product.quantity, 15)
        self.assertEqual(product.description, 'Teclado RGB con switches mecánicos')
        self.assertEqual(product.user, self.user)
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)

    def test_product_string_representation(self):
        """Verifica el método __str__ del producto."""
        product = Product.objects.create(
            name='Ratón Óptico',
            category='Periféricos',
            quantity=50,
            user=self.user
        )
        expected_str = "Ratón Óptico (50 uds.) — Periféricos"
        self.assertEqual(str(product), expected_str)
