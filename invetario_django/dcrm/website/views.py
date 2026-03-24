# Importa la función render, que permite combinar una plantilla HTML con datos y devolver una respuesta HTTP.
from django.shortcuts import render, redirect
# Importa el modelo User de Django, que representa a los usuarios en la base de datos.


# Importa funciones para autenticación de usuarios:
# - authenticate: verifica credenciales.
# - login: inicia sesión.
# - logout: cierra sesión.
from django.contrib.auth import authenticate, login, logout


# Importa el sistema de mensajes de Django para mostrar notificaciones al usuario.
from django.contrib import messages


# Aquí se deben crear las vistas de la aplicación.
# Esta función define la vista principal (home) del sitio.
def home(request):
    # Renderiza la plantilla 'home.html' y la retorna como respuesta HTTP.
    # No se pasan datos adicionales al contexto (diccionario vacío).
    if request.method == 'POST':
        # Si el método de la solicitud es POST, significa que se está enviando un formulario.
        # Aquí puedes manejar la lógica del formulario, como la autenticación de usuarios.
        username = request.POST['username'] # Obtiene el nombre de usuario del formulario.
        # Obtiene la contraseña del formulario.
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)# Verifica las credenciales del usuario.
        # Si el usuario es autenticado correctamente, se inicia sesión.
        if user is not None: # Si el usuario es autenticado correctamente.
            login(request, user)# Inicia sesión.
            # Muestra un mensaje de éxito al usuario.
            messages.success(request, "You Have Been Logged In!")# # Muestra un mensaje de éxito al usuario.
            return redirect('home')
        else:
            # Si las credenciales son incorrectas, se muestra un mensaje de error.
            messages.error(request, "Invalid Credentials!")
            # Muestra un mensaje de error al usuario.
            return redirect('home')
    else:
        # Si el método de la solicitud no es POST, simplemente renderiza la plantilla 'home.html'.
        return render(request, 'home.html', {})
# Esta función define la vista de inicio de sesión (login) del sitio.


def login_user(request):
    pass
def logout_user(request):
    pass