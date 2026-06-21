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


class SecurityAndRoleTest(TestCase):
    """Pruebas unitarias para la lógica de seguridad y roles (is_admin)."""

    def setUp(self):
        # Crear grupos de prueba
        self.admin_group = Group.objects.create(name='Administrador')
        self.operator_group = Group.objects.create(name='Operador')

        # Crear usuarios para cada rol
        self.admin_user = User.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            password='password123'
        )
        self.admin_user.groups.add(self.admin_group)

        self.operator_user = User.objects.create_user(
            username='operador2',
            email='op2@example.com',
            password='password123'
        )
        self.operator_user.groups.add(self.operator_group)

        self.regular_user = User.objects.create_user(
            username='regular',
            email='reg@example.com',
            password='password123'
        )

        self.staff_user = User.objects.create_user(
            username='staff1',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )

        self.superuser = User.objects.create_superuser(
            username='super',
            email='super@example.com',
            password='password123'
        )

    def test_is_admin_helper(self):
        """Verifica que la función helper is_admin reconozca correctamente los roles."""
        from website.views import is_admin

        # Administrador por pertenecer al grupo 'Administrador'
        self.assertTrue(is_admin(self.admin_user))

        # Administrador por ser staff
        self.assertTrue(is_admin(self.staff_user))

        # Administrador por ser superusuario
        self.assertTrue(is_admin(self.superuser))

        # Operador no es administrador
        self.assertFalse(is_admin(self.operator_user))

        # Usuario regular sin roles no es administrador
        self.assertFalse(is_admin(self.regular_user))

