# 📘 Explicación Completa del Código — Sistema de Inventario DCRM

Esta guía explica **línea por línea y archivo por archivo** todo el código del proyecto. Está diseñada para que cualquier integrante del equipo (o el evaluador) comprenda qué hace cada parte, por qué se tomó cada decisión técnica y cómo interactúan los componentes entre sí.

---

## 📁 Estructura General

```
invetario_django/
├── requirements.txt          ← dependencias pip
├── README.md                 ← documentación principal
├── docs/
│   ├── uml/                  ← diagramas PlantUML C1–C4
│   └── bitacoras/            ← bitácoras de trabajo
└── dcrm/                     ← proyecto Django
    ├── manage.py
    ├── .env
    ├── dcrm/                 ← configuración del proyecto
    │   ├── settings.py
    │   └── urls.py
    └── website/              ← aplicación principal
        ├── models.py
        ├── forms.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        ├── management/commands/setup_groups.py
        └── templates/
            ├── base.html
            ├── navbar.html
            ├── home.html
            ├── admin_dashboard.html
            ├── register.html
            └── static/
                ├── css/bootstrap.min.css  ← Bootstrap LOCAL
                ├── css/custom.css
                └── js/bootstrap.bundle.min.js ← Bootstrap LOCAL
```

---

## ⚙️ `dcrm/settings.py` — Configuración Central de Django

Este es el archivo más importante de configuración. Define cómo funciona todo el proyecto.

### Variables de entorno y seguridad
```python
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-dev-only')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
```
- `load_dotenv()` lee el archivo `.env` y carga las variables al sistema.
- `SECRET_KEY` nunca se escribe directamente en el código. Si no existe en `.env`, usa un valor de emergencia solo para desarrollo.
- `DEBUG = True` en desarrollo muestra errores detallados; en producción debe ser `False`.

### Aplicaciones instaladas
```python
INSTALLED_APPS = [
    'django.contrib.admin',       # Panel de administración integrado de Django
    'django.contrib.auth',        # Sistema de usuarios, grupos y permisos
    'django.contrib.contenttypes',
    'django.contrib.sessions',    # Manejo de sesiones de usuario
    'django.contrib.messages',    # Sistema de mensajes flash (alertas)
    'django.contrib.staticfiles', # Servir archivos CSS/JS locales
    'website',                    # Nuestra aplicación principal
]
```

### Middleware (capas de procesamiento de cada request)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',          # Seguridad HTTP
    'django.contrib.sessions.middleware.SessionMiddleware',   # Gestión de sesiones
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',             # Protección CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Autenticación
    'django.contrib.messages.middleware.MessageMiddleware',   # Mensajes flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Anti-clickjacking
]
```
Cada request HTTP pasa por todos estos middlewares en orden antes de llegar a la vista.

### Base de datos MySQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':     os.environ.get('DB_NAME', 'clientee'),
        'USER':     os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT':     os.environ.get('DB_PORT', '3306'),
    }
}
```
Todas las credenciales se leen del `.env`. Si no existen, usa valores predeterminados para desarrollo local.

### Archivos estáticos (Bootstrap LOCAL)
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'website', 'templates', 'static'),
]
```
Le dice a Django dónde encontrar los archivos CSS/JS locales. El `base.html` los carga con `{% static 'css/bootstrap.min.css' %}`.

### 4 Capas de seguridad en settings
```python
# Capa 1 — Sesiones y cookies seguras
SESSION_COOKIE_HTTPONLY = True   # JavaScript no puede leer la cookie de sesión
SESSION_COOKIE_AGE = 7200        # Sesión expira en 2 horas
SESSION_SAVE_EVERY_REQUEST = True # Renueva el timer en cada request
SESSION_COOKIE_SECURE = not DEBUG # Solo HTTPS en producción
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Capa 4 — Cabeceras HTTP de seguridad
SECURE_BROWSER_XSS_FILTER = True   # Cabecera X-XSS-Protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Cabecera X-Content-Type-Options
X_FRAME_OPTIONS = 'DENY'            # Previene clickjacking (iframes)
SECURE_SSL_REDIRECT = not DEBUG     # Redirige HTTP→HTTPS en producción
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # HSTS 1 año
```

---

## 🗄️ `website/models.py` — Definición de la Base de Datos

```python
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name      = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    category  = models.CharField(max_length=100, verbose_name="Categoría")
    quantity  = models.IntegerField(default=0, verbose_name="Cantidad")
    user      = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,  # Si el usuario se borra, sus productos también
                    related_name='products',
                    verbose_name="Usuario Registrador"
                )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    def __str__(self):
        return f"{self.name} ({self.quantity})"
```

**¿Qué crea esto en MySQL?**  
Una tabla `website_product` con columnas: `id`, `name`, `category`, `quantity`, `user_id` (FK a `auth_user`), `created_at`.

**Decisión clave**: `ForeignKey(User, on_delete=models.CASCADE)` — cada producto pertenece a exactamente un usuario. Esto es lo que permite filtrar `Product.objects.filter(user=request.user)` para mostrar solo los productos propios del Operador.

---

## 📝 `website/forms.py` — Formularios con Validación Regex

### Validadores globales (expresiones regulares)
```python
from django.core.validators import RegexValidator

# Solo letras con tildes y espacios — para nombres y apellidos
solo_letras = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
    message='Solo se permiten letras y espacios.'
)

# Letras, números, @/./+/-/_ — para nombre de usuario (estándar Django)
nombre_usuario_valido = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='El nombre de usuario solo puede contener letras, números y @/./+/-/_'
)

# Nombre de producto: letras, números, espacios, guiones y puntos
nombre_producto_valido = RegexValidator(
    regex=r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+$',
    message='Solo letras, números, espacios, guiones y puntos.'
)

# Categoría: solo letras y espacios
categoria_valida = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
    message='Solo letras y espacios.'
)
```

Los `RegexValidator` se ejecutan automáticamente cuando Django valida un formulario. Si el campo no coincide con la expresión regular, el formulario rechaza el dato con un mensaje de error claro.

### `SignUpForm` — Registro de usuarios
```python
class SignUpForm(UserCreationForm):  # Hereda de Django → Patrón Template Method
    email = forms.EmailField(...)
    first_name = forms.CharField(validators=[solo_letras], ...)
    last_name  = forms.CharField(validators=[solo_letras], ...)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
```

**`clean_email()`** — validación personalizada cruzada:
```python
def clean_email(self):
    email = self.cleaned_data.get('email', '').strip().lower()
    if User.objects.filter(email__iexact=email).exists():
        raise forms.ValidationError('Este correo ya está registrado.')
    return email
```
Antes de guardar, verifica que el correo no exista ya en la BD. `email__iexact` hace la comparación sin importar mayúsculas/minúsculas.

**`clean_username()`** — prohíbe espacios en el nombre de usuario:
```python
def clean_username(self):
    username = self.cleaned_data.get('username', '').strip()
    if ' ' in username:
        raise forms.ValidationError('El nombre de usuario no puede contener espacios.')
    return username
```

### `ProductForm` — Formulario de productos (Patrón ModelForm/DRY)
```python
class ProductForm(forms.ModelForm):
    name = forms.CharField(
        validators=[nombre_producto_valido],
        widget=forms.TextInput(attrs={
            'pattern': r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+',  # Validación HTML5
            'title': 'Solo letras, números, espacios, guiones y puntos.',
        })
    )
    ...
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity']
```

Al usar `forms.ModelForm` con `Meta.model = Product`, Django genera automáticamente el formulario basado en el modelo. Esto implementa el principio **DRY** (Don't Repeat Yourself): no hay que definir los campos dos veces.

**`clean_name()`** — longitud mínima:
```python
def clean_name(self):
    name = self.cleaned_data.get('name', '').strip()
    if len(name) < 2:
        raise forms.ValidationError('Mínimo 2 caracteres.')
    return name
```

**`clean_quantity()`** — evitar negativos:
```python
def clean_quantity(self):
    qty = self.cleaned_data.get('quantity')
    if qty is None or qty < 0:
        raise forms.ValidationError('La cantidad no puede ser negativa.')
    return qty
```

---

## 🎮 `website/views.py` — Controladores (Lógica de Negocio)

Este es el archivo más importante del sistema. Contiene toda la lógica de negocio.

### Helper `is_admin()` — Patrón Facade
```python
def is_admin(user):
    """
    Patrón Facade: encapsula 3 verificaciones de rol en 1 función.
    En lugar de repetir estas 3 condiciones en cada vista, llamamos is_admin().
    """
    return (
        user.is_superuser                              # Superadmin de Django
        or user.is_staff                               # Staff de Django
        or user.groups.filter(name='Administrador').exists()  # Grupo personalizado
    )
```

Sin este patrón, en cada vista tendríamos que repetir las 3 condiciones. Con Facade, cualquier cambio en la lógica de roles se hace en un solo lugar.

### Vista `home()` — Punto de entrada principal
```python
def home(request):
    # Manejar el formulario de LOGIN (POST sin 'action' específico)
    if request.method == 'POST' and 'action' not in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "¡Sesión iniciada correctamente!")
            if is_admin(user):
                return redirect('admin_dashboard')  # Admin → su panel
            return redirect('home')                 # Operador → su dashboard
        else:
            messages.error(request, "¡Credenciales inválidas!")
            return redirect('home')
    else:
        if request.user.is_authenticated:
            if is_admin(request.user):
                return redirect('admin_dashboard')
            # Operador: cargar SOLO sus productos
            products = Product.objects.filter(user=request.user).order_by('-created_at')
            # ... calcular estadísticas y pasar contexto al template
            return render(request, 'home.html', context)
        else:
            return render(request, 'home.html', {})  # Mostrar pantalla de login
```

**Flujo de decisión**:
1. ¿Es POST con credenciales? → Intentar login → Redirigir por rol
2. ¿Está autenticado? → Si es admin, redirigir. Si es operador, cargar su dashboard
3. ¿No autenticado? → Mostrar pantalla de login (home.html vacío)

### Vista `register_user()` — Patrón Observer
```python
def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario en la BD

            # PATRÓN OBSERVER: tras el evento "usuario creado", asignar rol automáticamente
            try:
                op_group = Group.objects.get(name='Operador')
                user.groups.add(op_group)  # Todo nuevo usuario = Operador por defecto
            except Group.DoesNotExist:
                pass  # Si el grupo no existe, no fallar

            # Auto-login tras registro exitoso
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido {username}!")
                return redirect('home')
        else:
            messages.error(request, "Error en el formulario.")
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})
```

El **Patrón Observer** aquí: cuando se crea un usuario (evento), la vista "observa" ese evento y reacciona asignando automáticamente el grupo 'Operador'. El usuario nunca tiene que elegir su rol; se asigna automáticamente.

### Vista `admin_dashboard()` — Control de acceso
```python
@login_required  # Capa 2: requiere autenticación
def admin_dashboard(request):
    if not is_admin(request.user):  # Capa 2: requiere rol de admin
        messages.error(request, "⛔ Acceso denegado.")
        return redirect('home')

    # Consultar TODOS los productos (sin filtro de usuario)
    products = Product.objects.select_related('user').all().order_by('-created_at')
    # select_related('user') optimiza la consulta SQL: hace JOIN en lugar de N+1 queries
    ...
```

`@login_required` redirige automáticamente a `LOGIN_URL = 'home'` si el usuario no está autenticado. La segunda verificación `if not is_admin(...)` asegura que aunque un Operador autenticado acceda a la URL directamente, sea bloqueado.

### CRUD de Productos con seguridad por propietario

**`add_product()`**:
```python
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)  # No guardar aún en BD
            product.user = request.user         # Asignar el usuario actual como propietario
            product.save()                      # Ahora sí guardar
            messages.success(request, f"Producto '{product.name}' registrado.")
        else:
            # Recolectar todos los errores y mostrarlos juntos
            errores = [err for field_errors in form.errors.values() for err in field_errors]
            messages.error(request, "Error: " + " | ".join(errores))
    ...
```

`commit=False` es clave: permite modificar el objeto antes de guardarlo. Así podemos inyectar `product.user = request.user` que no viene del formulario (evitando que un atacante envíe un `user_id` falsificado en el POST).

**`delete_product()` con seguridad de propietario**:
```python
@login_required
def delete_product(request, pk):
    # CAPA 2 DE SEGURIDAD: filtrar por propietario si es operador
    if is_admin(request.user):
        product = get_object_or_404(Product, pk=pk)        # Admin puede borrar cualquiera
    else:
        product = get_object_or_404(Product, pk=pk, user=request.user)  # Operador solo los suyos

    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Producto '{product.name}' eliminado.")
    ...
```

Si un Operador intenta borrar `delete_product/999/` (ID de otro usuario), la consulta `get_object_or_404(Product, pk=999, user=request.user)` fallará y Django devolverá 404. No hay mensaje de "no autorizado" (evita revelar información).

**`promote_user()`** — gestión de roles:
```python
@login_required
def promote_user(request, pk):
    if not is_admin(request.user): ...   # Solo admins
    target_user = get_object_or_404(User, pk=pk)

    if target_user == request.user:       # No puede degradarse a sí mismo
        messages.warning(...)
        return redirect('admin_dashboard')

    if target_user.is_superuser:          # No puede tocar superusuarios
        messages.warning(...)
        return redirect('admin_dashboard')

    admin_group = get_object_or_404(Group, name='Administrador')
    if target_user.groups.filter(name='Administrador').exists():
        target_user.groups.remove(admin_group)    # Degradar a Operador
    else:
        target_user.groups.add(admin_group)        # Promover a Administrador
```

### Exportaciones

**`export_csv()`** — con BOM para Excel:
```python
@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="inventario_{...}.csv"'
    response.write('\ufeff')  # BOM UTF-8: hace que Excel abra ñ y tildes correctamente
    writer = csv.writer(response)
    writer.writerow(['Producto', 'Categoría', 'Cantidad', 'Registrado por', 'Fecha'])
    ...
```

El caracter `\ufeff` es el **BOM (Byte Order Mark)** de UTF-8. Sin él, Excel en Windows no reconoce tildes y caracteres especiales del español.

**`export_pdf()`** — con ReportLab:
La función construye un PDF profesional con:
- Tabla resumen (total productos, unidades, categorías, stock bajo)
- Tabla completa del inventario con colores condicionales:
  - Rojo = cantidad 0
  - Naranja = cantidad ≤5
  - Normal = cantidad >5
- Pie de página con fecha y nombre del sistema

---

## 🌐 `website/urls.py` — Enrutador de la Aplicación

```python
from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.home,            name='home'),
    path('login/',                   views.login_user,      name='login'),
    path('logout/',                  views.logout_user,     name='logout'),
    path('register/',                views.register_user,   name='register'),
    # CRUD
    path('add_product/',             views.add_product,     name='add_product'),
    path('delete_product/<int:pk>/', views.delete_product,  name='delete_product'),
    path('edit_product/<int:pk>/',   views.edit_product,    name='edit_product'),
    # Reportes
    path('reportes/',                views.reportes,        name='reportes'),
    path('export_csv/',              views.export_csv,      name='export_csv'),
    path('export_pdf/',              views.export_pdf,      name='export_pdf'),
    # Dashboard Admin
    path('admin-dashboard/',         views.admin_dashboard, name='admin_dashboard'),
    path('promote-user/<int:pk>/',   views.promote_user,    name='promote_user'),
]
```

`<int:pk>` captura un número entero de la URL y lo pasa como parámetro `pk` a la vista. Si la URL contiene algo que no sea un entero, Django devuelve 404 automáticamente.

---

## 👥 `management/commands/setup_groups.py` — Patrón Command

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from website.models import Product

class Command(BaseCommand):
    help = 'Crea los grupos Administrador y Operador con sus permisos'

    def handle(self, *args, **options):
        # Crear grupo Administrador
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        # get_or_create: si ya existe, lo devuelve; si no, lo crea
        
        # Asignar todos los permisos sobre Product al grupo Administrador
        ct = ContentType.objects.get_for_model(Product)
        perms = Permission.objects.filter(content_type=ct)
        admin_group.permissions.set(perms)

        # Crear grupo Operador (sin permisos especiales)
        Group.objects.get_or_create(name='Operador')
        
        self.stdout.write(self.style.SUCCESS('Grupos creados exitosamente.'))
```

Este es el **Patrón Command**: encapsula una acción (crear grupos) como un comando reutilizable. Se ejecuta con `python manage.py setup_groups`.

---

## 🎨 Templates (Plantillas HTML)

### `base.html` — Patrón Template Method

```html
{% load static %}
<!doctype html>
<html lang="es" data-bs-theme="dark">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap 5 INSTALADO LOCALMENTE (no CDN) -->
    <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet">
    <!-- Google Fonts (Inter) para tipografía premium -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:..." rel="stylesheet">
  </head>
  <body>
    {% include 'navbar.html' %}   <!-- Incluye la navbar en TODAS las páginas -->
    <main>
      {% block content %}         <!-- Las demás plantillas inyectan su contenido aquí -->
      {% endblock %}
    </main>
    <!-- Bootstrap JS INSTALADO LOCALMENTE (incluye Popper para modales) -->
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
  </body>
</html>
```

`{% static 'css/bootstrap.min.css' %}` genera la URL `/static/css/bootstrap.min.css` que Django sirve desde la carpeta `static/`. Esto cumple el requisito de **Bootstrap Local** (sin CDN).

`data-bs-theme="dark"` activa el tema oscuro nativo de Bootstrap 5.3 en todo el sitio.

### `navbar.html` — Navegación dinámica por rol

La navbar detecta el rol del usuario y muestra diferentes opciones:

```html
{% if user.is_staff or user.is_superuser or user.groups.all.0.name == 'Administrador' %}
  <!-- LINKS DE ADMINISTRADOR: Inventario, Reportes, Usuarios, Admin Django -->
{% else %}
  <!-- LINKS DE OPERADOR (SPA): #inventario, #reportes via data-spa-section -->
  <a class="nav-link spa-link" id="nav-inventario" href="#" data-spa-section="inventario">
    📦 Inventario
  </a>
  <a class="nav-link spa-link" id="nav-reportes" href="#" data-spa-section="reportes">
    📊 Mis Reportes
  </a>
{% endif %}
```

Para el Operador, los links tienen `data-spa-section` que JavaScript usa para mostrar/ocultar secciones sin recargar la página.

### `home.html` — Dashboard del Operador (SPA)

Este template implementa la **Single Page Application** con varias secciones:

**Sección Inventario** (`id="section-inventario"`):
- Tarjetas de estadísticas personales (mis productos, mis unidades, mis categorías)
- Tabla de inventario con buscador en tiempo real
- Modales Bootstrap para agregar y editar productos (CRUD sin navegar a otra página)

**Sección Reportes** (`id="section-reportes"`, oculta por defecto):
- Gráfico de barras (unidades por categoría) con Chart.js
- Gráfico de dona (distribución) con Chart.js
- Tabla de stock bajo (alerta ≤5 unidades)
- Top 5 productos con más stock
- Actividad reciente

**JavaScript SPA** (dentro de home.html):
```javascript
function navigateSPA(section) {
    // 1. Ocultar TODAS las secciones
    document.querySelectorAll('.spa-section').forEach(el => el.style.display = 'none');
    
    // 2. Mostrar la sección destino con animación fade-in
    const target = document.getElementById('section-' + section);
    if (target) {
        target.style.display = 'block';
        target.style.opacity = '0';
        setTimeout(() => {
            target.style.transition = 'opacity 0.3s ease';
            target.style.opacity = '1';
        }, 10);
    }
    
    // 3. Actualizar link activo en navbar
    document.querySelectorAll('.spa-link').forEach(link => link.classList.remove('active'));
    document.getElementById('nav-' + section)?.classList.add('active');
    
    // 4. Actualizar URL del navegador SIN recargar (History API)
    history.pushState(null, '', '#' + section);
    
    // 5. Inicializar Chart.js solo la primera vez que se ve la sección reportes
    if (section === 'reportes' && !chartsInitialized) {
        initCharts();
        chartsInitialized = true;  // Flag para no crear múltiples instancias
    }
}
```

**Validación JS en tiempo real** (en los modales de CRUD):
```javascript
const regexRules = {
    'add-name': {
        regex: /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]{2,200}$/,
        msg: 'Mínimo 2 caracteres. Solo letras, números, espacios, guiones y puntos.'
    },
    'add-category': {
        regex: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{1,100}$/,
        msg: 'Solo letras y espacios.'
    },
    'add-quantity': {
        regex: /^\d+$/,
        msg: 'Solo números enteros positivos.'
    }
};
```

Estas reglas se aplican en el evento `input` (mientras el usuario escribe) y `blur` (cuando el campo pierde el foco), mostrando feedback visual inmediato con las clases de Bootstrap `is-valid` / `is-invalid`.

### `admin_dashboard.html` — Dashboard del Administrador

Usa las **pestañas (tabs) de Bootstrap** para organizar tres secciones sin recargar:

```html
<ul class="nav nav-pills" id="adminTabs" role="tablist">
  <li><button data-bs-toggle="pill" data-bs-target="#pane-inventario">📦 Inventario</button></li>
  <li><button data-bs-toggle="pill" data-bs-target="#pane-reportes">📊 Reportes</button></li>
  <li><button data-bs-toggle="pill" data-bs-target="#pane-usuarios">👥 Usuarios</button></li>
</ul>

<div class="tab-content">
  <div class="tab-pane fade show active" id="pane-inventario">...</div>
  <div class="tab-pane fade" id="pane-reportes">...</div>
  <div class="tab-pane fade" id="pane-usuarios">...</div>
</div>
```

Bootstrap maneja automáticamente el show/hide de pestañas mediante `data-bs-toggle="pill"`.

**Gestión de usuarios en la pestaña Usuarios**:
```html
{% for info in users_info %}
  <!-- info viene del contexto: {'user': u, 'is_admin': bool, 'product_count': int} -->
  <td>
    {% if info.is_admin %}
      <span class="badge">👑 Administrador</span>
    {% else %}
      <span class="badge">🔧 Operador</span>
    {% endif %}
  </td>
  <td>
    {% if info.user == user %}
      <span>Tu cuenta</span>  <!-- No mostrar botón de cambio de rol para sí mismo -->
    {% elif info.user.is_superuser %}
      <span>—</span>          <!-- No tocar superusuarios -->
    {% else %}
      <form method="post" action="{% url 'promote_user' info.user.pk %}">
        {% csrf_token %}
        {% if info.is_admin %}
          <button>⬇️ Hacer Operador</button>
        {% else %}
          <button>👑 Hacer Admin</button>
        {% endif %}
      </form>
    {% endif %}
  </td>
{% endfor %}
```

### `register.html` — Formulario de Registro

Características destacadas:
- **Indicador de fortaleza de contraseña** en tiempo real (5 niveles: muy débil → muy fuerte)
- **Toggle de visibilidad** de contraseña (botón 👁️)
- **Validación de coincidencia** de contraseñas en tiempo real
- **Todos los campos con Regex** tanto en HTML5 (`pattern`) como en JavaScript
- Errores del servidor se muestran si los hay (errores de validación backend)

---

## 🔒 `website/admin.py` — Panel de Administración Django

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'user', 'created_at']
    list_filter  = ['category', 'user']      # Filtros en barra lateral
    search_fields = ['name', 'category', 'user__username']  # Búsqueda por texto
    ordering = ['-created_at']               # Más recientes primero
    list_per_page = 25
    readonly_fields = ['created_at']         # Fecha no se puede editar manualmente
```

Esto registra el modelo `Product` en el panel `/admin/` de Django con configuración premium. Solo accesible para superusuarios.

---

## 🎨 `static/css/custom.css` — Estilos Premium

Este archivo contiene estilos personalizados que complementan Bootstrap:

- **Scrollbars personalizadas** con colores del tema oscuro del sistema
- **Animaciones hover** en las tarjetas (`hover-scale`: sube 4px con sombra)
- **Tablas oscuras** con filas alternadas y efectos
- **Inputs oscuros** con placeholder en color apropiado
- **Variables CSS** para mantener consistencia de colores en todo el sitio

---

## 🔗 Flujo Completo de una Operación (Ejemplo: Agregar Producto)

```
1. Usuario (Operador) hace clic en "➕ Nuevo Registro"
   → Bootstrap abre el modal #addProductModal (sin recargar página)

2. El usuario escribe en el campo "Nombre"
   → JS detecta evento 'input' → evalúa regex → muestra is-valid/is-invalid

3. El usuario hace clic en "💾 Guardar Producto"
   → JS valida todos los campos antes de enviar
   → Si algún campo falla: e.preventDefault() — DETIENE el envío
   → Si todo OK: el formulario envía POST a /add_product/

4. Django recibe el POST en add_product(request)
   → Verificación @login_required (sesión activa)
   → Instancia ProductForm(request.POST)
   → form.is_valid() ejecuta: RegexValidator + clean_name() + clean_quantity()
   → Si pasa: product.user = request.user → product.save()
   → messages.success("Producto registrado.")
   → redirect('home')  ← nueva petición GET

5. home(request) recarga el dashboard
   → messages aparecen como alertas verdes auto-dismissibles
   → La tabla de inventario ya tiene el nuevo producto
```

---

## 📊 Resumen de Patrones de Diseño

| Patrón | Tipo | Archivo | Descripción |
|---|---|---|---|
| **MVT** | Arquitectónico | Todo el proyecto | Separación Model-View-Template de Django |
| **Facade** | Estructural | `views.py` → `is_admin()` | Encapsula lógica compleja de verificación de rol |
| **Observer** | Comportamental | `views.py` → `register_user()` | Asignación automática de rol tras evento de creación |
| **Template Method** | Estructural | `base.html` + hijos | Define esqueleto de página; hijos sobreescriben `{% block %}` |
| **Repository** | Estructural | `views.py` + ORM Django | Abstrae el acceso a datos con `Product.objects.filter()` |
| **ModelForm (DRY)** | Principio | `forms.py` | Genera formularios automáticamente desde los modelos |
| **Command** | Comportamental | `setup_groups.py` | Encapsula acción de inicialización como comando CLI |

---

## ✅ Verificación de Requerimientos

### 1. Login con Roles ✅
- `home()` maneja login y redirige por rol
- `is_admin()` verifica rol
- `@login_required` protege vistas

### 2. CRUD Completo ✅
- **Create**: `add_product()` + modal Bootstrap
- **Read**: `home()` y `admin_dashboard()` listan productos
- **Update**: `edit_product()` + modal Bootstrap
- **Delete**: `delete_product()` + confirmación JS

### 3. Menú SPA ✅
- Operador: `navigateSPA()` en `home.html`
- Admin: pestañas Bootstrap en `admin_dashboard.html`
- History API: `history.pushState()` actualiza URL sin recargar

### 4. Alertas ✅
- `messages.success()`, `messages.error()`, `messages.warning()` en todas las acciones
- Renderizadas en templates con clase Bootstrap `alert-success/danger/warning`
- Auto-dismissible con `alert-dismissible` y botón ×
- Feedback visual en tiempo real en formularios (is-valid / is-invalid)

### 5. Bootstrap Local ✅
- `static/css/bootstrap.min.css` → 232KB instalado localmente
- `static/js/bootstrap.bundle.min.js` → 80KB instalado localmente
- Cargados con `{% static %}` sin CDN en `base.html`

### 6. Validaciones con Regex ✅
- **Backend**: `RegexValidator` en `forms.py` para todos los campos
- **Frontend**: atributo `pattern` en HTML5 + validación JS en tiempo real
- **Campos protegidos**: username, password, nombre, apellido, email, nombre producto, categoría

### 7. Seguridad en campos críticos ✅
- Username: solo `[\w.@+-]+` (sin caracteres de inyección)
- Password: mínimo 8 chars, no numérica pura, validadores Django
- Todos los campos con `maxlength` estricto

### 8. 4 Capas de Seguridad ✅
- **Capa 1**: Sesiones/cookies HttpOnly, expiración 2h, renovación automática
- **Capa 2**: `@login_required` + `is_admin()` + filtrado por propietario en BD
- **Capa 3**: `RegexValidator` + `clean_*()` + CSRF token en todos los formularios
- **Capa 4**: Headers HTTP seguros (XSS, MIME, Clickjacking, HSTS en producción)
