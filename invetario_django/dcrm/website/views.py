from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product
from django.db.models import Sum

def home(request):
    if request.method == 'POST' and 'action' not in request.POST:
        # Autenticación de usuario normal
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "¡Sesión iniciada correctamente!")
            return redirect('home')
        else:
            messages.error(request, "¡Credenciales inválidas!")
            return redirect('home')
    else:
        # Si está logueado mostramos el dashboard con los productos
        if request.user.is_authenticated:
            products = Product.objects.all().order_by('-created_at')
            total_products = products.count()
            context = {
                'products': products,
                'total_products': total_products,
            }
            return render(request, 'home.html', context)
        else:
            return render(request, 'home.html', {})
def login_user(request):
    return redirect('home')

def logout_user(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('home')

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        
        if name and category and quantity:
            Product.objects.create(
                name=name,
                category=category,
                quantity=quantity,
                user=request.user
            )
            messages.success(request, "Producto registrado correctamente.")
        else:
            messages.error(request, "Faltan campos por llenar para el registro.")
            
    return redirect('home')

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"El producto {product.name} ha sido eliminado.")
    return redirect('home')