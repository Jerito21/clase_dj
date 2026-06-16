"""
Comando de gestión: setup_groups
Crea los grupos de roles del sistema (Administrador y Operador)
y les asigna los permisos correspondientes sobre el modelo Product.

Uso:
    python manage.py setup_groups
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Crea los grupos de roles: Administrador y Operador'

    def handle(self, *args, **options):
        self.stdout.write('\n[*] Configurando grupos y roles del sistema...\n')

        try:
            from website.models import Product

            content_type = ContentType.objects.get_for_model(Product)
            all_perms = Permission.objects.filter(content_type=content_type)

            # Grupo Administrador: control total sobre todos los productos
            admin_group, created = Group.objects.get_or_create(name='Administrador')
            admin_group.permissions.set(all_perms)
            status = 'creado' if created else 'ya existia (actualizado)'
            self.stdout.write(self.style.SUCCESS(f'   [OK] Grupo "Administrador" {status}.'))
            self.stdout.write('      Permisos: ver, agregar, editar y eliminar CUALQUIER producto.')

            # Grupo Operador: permisos basicos (solo sus propios productos en la logica de vistas)
            op_group, created = Group.objects.get_or_create(name='Operador')
            op_perms = all_perms.filter(
                codename__in=['add_product', 'change_product', 'delete_product', 'view_product']
            )
            op_group.permissions.set(op_perms)
            status = 'creado' if created else 'ya existia (actualizado)'
            self.stdout.write(self.style.SUCCESS(f'   [OK] Grupo "Operador" {status}.'))
            self.stdout.write('      Permisos: ver, agregar, editar y eliminar sus PROPIOS productos.')

            self.stdout.write('\n[INFO] Proximos pasos:')
            self.stdout.write('   Los nuevos usuarios registrados reciben automaticamente el rol "Operador".')
            self.stdout.write('   Para promover un usuario a Administrador:')
            self.stdout.write(self.style.WARNING(
                '\n   python manage.py shell\n'
                '   >>> from django.contrib.auth.models import User, Group\n'
                '   >>> user = User.objects.get(username="nombre_del_usuario")\n'
                '   >>> grupo = Group.objects.get(name="Administrador")\n'
                '   >>> user.groups.add(grupo)\n'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] al crear grupos: {e}'))
            raise
