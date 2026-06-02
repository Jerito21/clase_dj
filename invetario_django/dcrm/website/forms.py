#website/forms.py
# Importación de librerías y funciones para la creación de formularios en Django
from django import forms  # para crear formularios en Django y sus campos.
from django.contrib.auth.forms import UserCreationForm  # formulario de registro basado en el modelo User de Django.
from django.contrib.auth.models import User  # modelo de usuario de Django.
# Nota: Record no existe en este proyecto. El modelo principal es Product.
# Si en el futuro se necesita un formulario basado en Product, se importaría así:
# from .models import Product


# Formulario de registro de usuarios personalizado que hereda de UserCreationForm
class SignUpForm(UserCreationForm):
    # Campo adicional: correo electrónico
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg rounded-3 border-0',
            'placeholder': 'Correo electrónico',
        })
    )

    # Campos de nombre y apellido
    first_name = forms.CharField(
        label='',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-3 border-0',
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label='',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-3 border-0',
            'placeholder': 'Apellido',
        })
    )

    class Meta:
        # Especifica que el modelo asociado es el modelo User de Django
        model = User
        # Campos que se incluirán en el formulario de registro
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs) -> None:
        # Llama al constructor de la clase padre (UserCreationForm)
        super(SignUpForm, self).__init__(*args, **kwargs)

        # --- Campo: username ---
        self.fields['username'].widget.attrs['class'] = 'form-control form-control-lg rounded-3 border-0'
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
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