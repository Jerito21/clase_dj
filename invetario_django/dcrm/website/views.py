from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import SignUpForm, ProductForm
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
        if request.user.is_authenticated:
            products = Product.objects.all().order_by('-created_at')
            total_products = products.count()
            total_categories = Product.objects.values('category').distinct().count()

            # ── Datos de Reportes para SPA ──────────────────────────────────
            total_units = products.aggregate(total=Sum('quantity'))['total'] or 0

            by_category = (
                products.values('category')
                .annotate(count=Count('id'), total_qty=Sum('quantity'))
                .order_by('-total_qty')
            )

            by_user = (
                products.values('user__username')
                .annotate(count=Count('id'), total_qty=Sum('quantity'))
                .order_by('-count')
            )

            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_count = products.filter(created_at__gte=seven_days_ago).count()

            low_stock = products.filter(quantity__lte=5).order_by('quantity')
            top_stock = products.order_by('-quantity')[:5]
            recent_activity = products.order_by('-created_at')[:10]

            chart_labels = [item['category'] for item in by_category]
            chart_data = [item['total_qty'] for item in by_category]
            chart_counts = [item['count'] for item in by_category]
            # ─────────────────────────────────────────────────────────────────

            context = {
                'products': products,
                'total_products': total_products,
                'total_categories': total_categories,
                # Reportes
                'total_units': total_units,
                'by_category': by_category,
                'by_user': by_user,
                'recent_count': recent_count,
                'low_stock': low_stock,
                'top_stock': top_stock,
                'recent_activity': recent_activity,
                'chart_labels': chart_labels,
                'chart_data': chart_data,
                'chart_counts': chart_counts,
                # Formulario de producto (vacío para el modal de agregar)
                'product_form': ProductForm(),
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
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
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
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, f"Producto '{product.name}' registrado correctamente.")
        else:
            # Recopilar errores del formulario para mostrarlos
            errores = []
            for field, error_list in form.errors.items():
                for error in error_list:
                    errores.append(error)
            messages.error(request, "Error de validación: " + " | ".join(errores))
    return redirect('home')


@login_required
def delete_product(request, pk):
    # Solo el dueño del producto puede eliminarlo
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"El producto '{product.name}' ha sido eliminado.")
    return redirect('home')


@login_required
def edit_product(request, pk):
    # Solo el dueño del producto puede editarlo
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"El producto '{product.name}' ha sido actualizado correctamente.")
        else:
            errores = []
            for field, error_list in form.errors.items():
                for error in error_list:
                    errores.append(error)
            messages.error(request, "Error de validación: " + " | ".join(errores))
    return redirect('home')


@login_required
def reportes(request):
    """Vista de reportes – mantiene la URL directa para compatibilidad."""
    return redirect('home')


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