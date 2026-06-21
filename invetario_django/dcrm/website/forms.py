#website/forms.py
"""
Formularios del sistema de inventario.
Implementa el patrón ModelForm (DRY) para generación automática
de formularios validados desde los modelos, con expresiones regulares
tanto a nivel de validador Python como de atributos HTML5.
"""
# Importación de librerías y funciones para la creación de formularios en Django
from django import forms  # para crear formularios en Django y sus campos.
from django.contrib.auth.forms import UserCreationForm  # formulario de registro basado en el modelo User de Django.
from django.contrib.auth.models import User  # modelo de usuario de Django.
from django.core.validators import RegexValidator  # para validar campos con expresiones regulares.
from .models import Product



# ─── Validadores con Expresiones Regulares ────────────────────────────────────

# Solo letras (con tildes/ñ) y espacios – para nombres y apellidos
solo_letras = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
    message='Solo se permiten letras y espacios. No uses números ni caracteres especiales.'
)

# Solo letras, números, puntos, guiones y guión bajo – para nombre de usuario
nombre_usuario_valido = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='El nombre de usuario solo puede contener letras, números y los caracteres @/./+/-/_'
)

# Nombre de producto: letras, números, espacios y guiones
nombre_producto_valido = RegexValidator(
    regex=r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+$',
    message='El nombre solo puede contener letras, números, espacios, guiones y puntos.'
)

# Categoría: letras y espacios únicamente
categoria_valida = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
    message='La categoría solo puede contener letras y espacios.'
)


# ─── Formulario de Registro de Usuario ───────────────────────────────────────

class SignUpForm(UserCreationForm):
    """Formulario de registro de usuarios con validaciones mediante expresiones regulares."""

    # Campo adicional: correo electrónico
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg rounded-3 border-0',
            'placeholder': 'Correo electrónico',
            'pattern': r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
            'title': 'Ingresa un correo electrónico válido (ej. usuario@dominio.com)',
        })
    )

    # Campo nombre con validación de expresión regular
    first_name = forms.CharField(
        label='',
        max_length=30,
        validators=[solo_letras],
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-3 border-0',
            'placeholder': 'Nombre',
            'pattern': r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+',
            'title': 'Solo letras y espacios. Sin números ni caracteres especiales.',
        })
    )

    # Campo apellido con validación de expresión regular
    last_name = forms.CharField(
        label='',
        max_length=30,
        validators=[solo_letras],
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-3 border-0',
            'placeholder': 'Apellido',
            'pattern': r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+',
            'title': 'Solo letras y espacios. Sin números ni caracteres especiales.',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs) -> None:
        super(SignUpForm, self).__init__(*args, **kwargs)

        # --- Campo: username ---
        self.fields['username'].validators.append(nombre_usuario_valido)
        self.fields['username'].widget.attrs['class'] = 'form-control form-control-lg rounded-3 border-0'
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['username'].widget.attrs['pattern'] = r'[\w.@+-]+'
        self.fields['username'].widget.attrs['title'] = 'Solo letras, números y @/./+/-/_'
        self.fields['username'].label = ''
        self.fields['username'].help_text = (
            '<span class="text-muted small">Requerido. 150 caracteres máximo. '
            'Solo letras, números y @/./+/-/_</span>'
        )

        # --- Campo: password1 (contraseña) ---
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-lg rounded-3 border-0'
        self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = (
            '<span class="text-muted small">Mínimo 8 caracteres. '
            'No puede ser completamente numérica.</span>'
        )

        # --- Campo: password2 (confirmar contraseña) ---
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-lg rounded-3 border-0'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirma tu contraseña'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = (
            '<span class="text-muted small">Ingresa la misma contraseña que antes, para verificación.</span>'
        )

    def clean_email(self):
        """Validación personalizada: el correo no puede estar ya registrado."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado en el sistema.')
        return email

    def clean_username(self):
        """Validación personalizada: el nombre de usuario no puede tener espacios."""
        username = self.cleaned_data.get('username', '').strip()
        if ' ' in username:
            raise forms.ValidationError('El nombre de usuario no puede contener espacios.')
        return username


# ─── Formulario de Producto con Expresiones Regulares ────────────────────────

class ProductForm(forms.ModelForm):
    """Formulario para crear/editar productos con validaciones regex."""

    name = forms.CharField(
        label='Nombre del Producto',
        max_length=200,
        validators=[nombre_producto_valido],
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary-subtle shadow-sm',
            'placeholder': 'Ej. Teclado Mecánico',
            'pattern': r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+',
            'title': 'Solo letras, números, espacios, guiones y puntos.',
        })
    )

    category = forms.CharField(
        label='Categoría',
        max_length=100,
        validators=[categoria_valida],
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary-subtle shadow-sm',
            'placeholder': 'Ej. Periféricos',
            'pattern': r'[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios.',
        })
    )

    quantity = forms.IntegerField(
        label='Cantidad en Stock',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary-subtle shadow-sm',
            'min': '0',
            'placeholder': '0',
        })
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('El nombre del producto debe tener al menos 2 caracteres.')
        return name

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return qty