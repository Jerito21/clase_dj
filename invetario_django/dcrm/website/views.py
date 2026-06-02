from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import SignUpForm
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv

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
            total_categories = Product.objects.values('category').distinct().count()
            context = {
                'products': products,
                'total_products': total_products,
                'total_categories': total_categories,
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


def register_user(request):
    """Vista de registro de nuevos usuarios usando SignUpForm."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # guarda el nuevo usuario en la base de datos
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # autenticar e iniciar sesión automáticamente
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido {username}! Tu cuenta ha sido creada correctamente.")
                return redirect('home')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})

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


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')

        if name and category and quantity:
            product.name = name
            product.category = category
            product.quantity = quantity
            product.save()
            messages.success(request, f"El producto '{product.name}' ha sido actualizado correctamente.")
        else:
            messages.error(request, "Faltan campos por llenar para la edición.")

    return redirect('home')


@login_required
def reportes(request):
    """Vista principal de reportes con estadísticas del inventario."""
    products = Product.objects.all()
    
    # Estadísticas generales
    total_products = products.count()
    total_units = products.aggregate(total=Sum('quantity'))['total'] or 0
    total_categories = products.values('category').distinct().count()
    
    # Productos por categoría
    by_category = (
        products.values('category')
        .annotate(
            count=Count('id'),
            total_qty=Sum('quantity')
        )
        .order_by('-total_qty')
    )
    
    # Productos por usuario
    by_user = (
        products.values('user__username')
        .annotate(
            count=Count('id'),
            total_qty=Sum('quantity')
        )
        .order_by('-count')
    )
    
    # Últimos 7 días
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_count = products.filter(created_at__gte=seven_days_ago).count()
    
    # Productos con stock bajo (cantidad <= 5)
    low_stock = products.filter(quantity__lte=5).order_by('quantity')
    
    # Top 5 productos con mayor stock
    top_stock = products.order_by('-quantity')[:5]
    
    # Actividad reciente (últimos 10 registros)
    recent_activity = products.order_by('-created_at')[:10]
    
    # Datos para la gráfica de categorías (JSON para Chart.js)
    chart_labels = [item['category'] for item in by_category]
    chart_data = [item['total_qty'] for item in by_category]
    chart_counts = [item['count'] for item in by_category]
    
    context = {
        'total_products': total_products,
        'total_units': total_units,
        'total_categories': total_categories,
        'by_category': by_category,
        'by_user': by_user,
        'recent_count': recent_count,
        'low_stock': low_stock,
        'top_stock': top_stock,
        'recent_activity': recent_activity,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'chart_counts': chart_counts,
    }
    return render(request, 'reportes.html', context)


@login_required
def export_csv(request):
    """Exportar todo el inventario como archivo CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="inventario_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff')  # BOM para compatibilidad con Excel
    
    writer = csv.writer(response)
    writer.writerow(['Producto', 'Categoría', 'Cantidad', 'Registrado por', 'Fecha de Registro'])
    
    products = Product.objects.all().order_by('-created_at')
    for p in products:
        writer.writerow([
            p.name,
            p.category,
            p.quantity,
            p.user.username,
            p.created_at.strftime('%d/%m/%Y %H:%M'),
        ])
    
    return response