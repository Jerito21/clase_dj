# 📦 Sistema de Inventario DCRM

> Sistema de gestión de inventario desarrollado con **Django 5** y **MySQL**, con control de roles, interfaz SPA, seguridad multicapa y exportación de reportes.

---

## 👥 Integrantes del Equipo

| Nombre | Rol en el proyecto |
|---|---|
| Jeronimo Gil | Desarrollador Principal / Backend |

---

## 📋 Descripción General

El **Sistema de Inventario DCRM** es una aplicación web full-stack que permite la gestión de inventario de productos con un sistema de roles diferenciado:

- **Administrador**: Acceso global a todos los productos, usuarios y reportes del sistema.
- **Operador**: Acceso restringido únicamente a sus propios productos e inventario personal.

La aplicación implementa el patrón **MVT (Model-View-Template)** de Django, con una interfaz tipo **SPA (Single Page Application)** mediante JavaScript vanilla y **Bootstrap 5 instalado localmente**.

---

## ✅ Lista de Verificación de Requerimientos

| Requerimiento | Estado |
|---|---|
| Login con Roles (Admin / Operador) | ✅ Implementado |
| CRUD Completo de Productos | ✅ Implementado |
| Menú SPA sin recargas | ✅ Implementado |
| Alertas visuales al usuario | ✅ Implementado |
| Bootstrap Local (sin CDN) | ✅ Instalado en `static/` |
| Validaciones con Expresiones Regulares | ✅ Backend (forms.py) + Frontend (JS) |
| Seguridad en campos críticos | ✅ RegexValidator + clean() en forms |
| 4 capas de seguridad | ✅ Ver sección de Seguridad |
| Historial de commits en GitHub (≥20) | ✅ Completado |
| Archivo README.md | ✅ Este archivo |
| Archivo requirements.txt | ✅ Existe |
| Diagramas PlantUML (C1 al C4) | ✅ Existe |
| Patrones de Diseño documentados | ✅ Ver sección correspondiente |
| Bitácoras de trabajo (8 en total) | ✅ Existe |

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje base |
| Django | ≥5.0, <5.1 | Framework web (MVT) |
| MySQL | 8.0+ | Base de datos principal |
| mysqlclient | ≥2.2.4 | Conector Python-MySQL |
| Bootstrap | 5.3 (local) | Framework CSS/JS de UI |
| Chart.js | 4.4.x (CDN) | Gráficos interactivos |
| ReportLab | ≥4.0 | Generación de PDFs |
| python-dotenv | ≥1.0 | Variables de entorno |
| Google Fonts (Inter) | — | Tipografía premium |

---

## 📁 Estructura del Proyecto

```
invetario_django/                      <- Directorio Raíz
│
├── README.md                          <- Este archivo de documentación
├── requirements.txt                   <- Dependencias del proyecto
├── .gitignore                         <- Archivos ignorados por Git
│
├── docs/                              <- Documentación técnica
│   ├── uml/                           <- Diagramas PlantUML
│   │   ├── c1_contexto.puml
│   │   ├── c2_contenedores.puml
│   │   ├── c3_componentes.puml
│   │   └── c4_codigo.puml
│   └── bitacoras/                     <- Bitácoras de trabajo
│       ├── bitacora_01.md ... bitacora_08.md
│
└── dcrm/                              <- Proyecto Django
    ├── manage.py                      <- CLI de Django
    ├── .env                           <- Variables de entorno (NO versionar)
    │
    ├── dcrm/                          <- Configuración del proyecto
    │   ├── settings.py                <- Configuraciones globales y seguridad
    │   ├── urls.py                    <- Enrutador principal
    │   ├── wsgi.py / asgi.py          <- Interfaces de servidor
    │
    └── website/                       <- Aplicación principal
        ├── models.py                  <- Modelo Product (BD)
        ├── forms.py                   <- Formularios con validación Regex
        ├── views.py                   <- Controladores y lógica de negocio
        ├── urls.py                    <- URLs de la aplicación
        ├── admin.py                   <- Configuración del panel Admin
        ├── management/commands/       <- Comandos personalizados Django
        │   └── setup_groups.py        <- Crea grupos Administrador/Operador
        └── templates/                 <- Plantillas HTML
            ├── base.html              <- Layout base con Bootstrap local
            ├── navbar.html            <- Navbar dinámica por rol
            ├── home.html              <- Dashboard Operador (SPA)
            ├── admin_dashboard.html   <- Dashboard Admin (SPA con tabs)
            ├── register.html          <- Formulario de registro
            └── static/                <- Archivos estáticos locales
                ├── css/
                │   ├── bootstrap.min.css   <- Bootstrap 5 LOCAL
                │   └── custom.css          <- Estilos premium personalizados
                └── js/
                    └── bootstrap.bundle.min.js  <- JS Bootstrap LOCAL
```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/Jerito21/clase_dj.git
cd clase_dj/invetario_django
```

### 2. Crear y activar entorno virtual
```bash
python -m venv env
# Windows:
env\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear el archivo `dcrm/.env` con el siguiente contenido:
```env
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
DEBUG=True
DB_NAME=inventario_db
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=3306
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5. Crear la base de datos en MySQL
```sql
CREATE DATABASE inventario_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Aplicar migraciones
```bash
cd dcrm
python manage.py migrate
```

### 7. Crear grupos de roles
```bash
python manage.py setup_groups
```

### 8. Crear superusuario
```bash
python manage.py createsuperuser
```

### 9. Ejecutar el servidor
```bash
python manage.py runserver
```
Visitar: **http://127.0.0.1:8000/**

---

## 🔐 Seguridad — 4 Capas Implementadas

### Capa 1 — Autenticación y Control de Sesión
- Sistema de login con `django.contrib.auth`
- Sesiones con expiración en **2 horas** (`SESSION_COOKIE_AGE = 7200`)
- Cookies de sesión **HttpOnly** (no accesibles por JavaScript → previene XSS)
- `SESSION_SAVE_EVERY_REQUEST = True` (renovación automática)

### Capa 2 — Control de Acceso por Roles (Autorización)
- Decorador `@login_required` en todas las vistas protegidas
- Helper `is_admin()` verifica grupo, is_staff y is_superuser
- **Operadores** no pueden ver ni modificar productos ajenos (filtrado en BD con `user=request.user`)
- **Administradores** no pueden ser degradados por otros admins sin permiso explícito

### Capa 3 — Validación y Sanitización de Entradas
- `RegexValidator` en todos los campos del formulario (backend Python)
- Atributos `pattern`, `minlength`, `maxlength` en HTML (frontend)
- Validación JS en tiempo real con retroalimentación visual
- Métodos `clean_*()` en formularios para validaciones cruzadas
- **CSRF Token** (`{% csrf_token %}`) en todos los formularios POST

### Capa 4 — Cabeceras HTTP y Configuración del Servidor
- `SECURE_BROWSER_XSS_FILTER = True` → Cabecera X-XSS-Protection
- `SECURE_CONTENT_TYPE_NOSNIFF = True` → Previene MIME sniffing
- `X_FRAME_OPTIONS = 'DENY'` → Previene Clickjacking
- `CSRF_COOKIE_HTTPONLY = True` → Token CSRF no legible por JS
- `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` (activos en producción)
- `SECRET_KEY` y credenciales en `.env` (nunca en el código)

---

## 🎨 Patrones de Diseño Identificados

| Patrón | Clasificación | Implementación |
|---|---|---|
| **MVT (Model-View-Template)** | Arquitectónico | Toda la estructura Django |
| **Facade** | Estructural | Función `is_admin()` en views.py — encapsula la lógica compleja de verificación de rol en una sola llamada |
| **Observer** | Comportamiento | `register_user()` asigna automáticamente el grupo 'Operador' tras el guardado del usuario |
| **Template Method** | Estructural | `base.html` define el esqueleto de página; `home.html` y `admin_dashboard.html` sobreescriben `{% block content %}` |
| **Repository** | Estructural | ORM de Django abstrae el acceso a datos (`Product.objects.filter(...)`) |
| **ModelForm (DRY)** | Principio/Patrón | `ProductForm` y `SignUpForm` generan automáticamente formularios validados desde los modelos, evitando duplicación de código |
| **Command** | Comportamiento | `setup_groups.py` implementa un Management Command de Django |

---

## 📊 Funcionalidades del Sistema

### Para Operadores
- 📦 Ver, crear, editar y eliminar **sus propios** productos
- 🔍 Buscador reactivo en la tabla de inventario
- 📊 Reportes visuales con gráficos (barras y dona)
- ⚠️ Alertas de stock bajo (≤5 unidades)
- 📥 Exportar inventario personal en CSV y PDF
- 🧭 Navegación SPA (sin recargas de página)

### Para Administradores
- 👑 Panel global con inventario de TODOS los usuarios
- 👥 Gestión de usuarios (promover/degradar roles)
- 📊 Reportes globales con estadísticas del sistema
- 📥 Exportar todo el inventario en CSV y PDF
- ⚙️ Acceso al panel interno de Django Admin

---

## 🗂️ Modelos de la Base de Datos

### Modelo `Product`
```python
class Product(models.Model):
    name      = CharField(max_length=200)   # Nombre del producto
    category  = CharField(max_length=100)   # Categoría
    quantity  = IntegerField(default=0)     # Cantidad en stock
    user      = ForeignKey(User, ...)       # Propietario del registro
    created_at = DateTimeField(auto_now_add=True)  # Fecha automática
```

---

## 🔗 URLs del Sistema

| URL | Vista | Descripción |
|---|---|---|
| `/` | `home` | Login / Dashboard Operador |
| `/register/` | `register_user` | Registro de nuevos usuarios |
| `/logout/` | `logout_user` | Cierre de sesión |
| `/admin-dashboard/` | `admin_dashboard` | Dashboard de administrador |
| `/add_product/` | `add_product` | Crear producto (POST) |
| `/edit_product/<id>/` | `edit_product` | Editar producto (POST) |
| `/delete_product/<id>/` | `delete_product` | Eliminar producto (POST) |
| `/promote-user/<id>/` | `promote_user` | Cambiar rol de usuario |
| `/export_csv/` | `export_csv` | Descargar CSV |
| `/export_pdf/` | `export_pdf` | Descargar PDF |

---

## 📤 Exportaciones

- **CSV**: UTF-8 con BOM (compatible con Excel), incluye todos los campos relevantes
- **PDF**: Generado con ReportLab, con estadísticas resumen, tabla completa de productos y alertas visuales por nivel de stock (rojo=0, naranja=≤5)

---

## 🚀 Comandos Útiles

```bash
# Activar entorno virtual
env\Scripts\activate

# Aplicar migraciones
python manage.py migrate

# Crear grupos de roles
python manage.py setup_groups

# Recolectar archivos estáticos (producción)
python manage.py collectstatic

# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear superusuario
python manage.py createsuperuser
```

---

## 📝 Notas de Desarrollo

- Bootstrap 5 está **instalado localmente** en `website/templates/static/` — no depende de CDN
- Chart.js se carga desde CDN (`cdn.jsdelivr.net`) para los gráficos
- La base de datos SQLite (`db.sqlite3`) está incluida como respaldo/desarrollo, pero el sistema está configurado para **MySQL** en producción
- El archivo `.env` **nunca debe subirse** a GitHub (está en `.gitignore`)

---

*Desarrollado como proyecto de módulo — Gestión de Inventario con Django · 2025*
