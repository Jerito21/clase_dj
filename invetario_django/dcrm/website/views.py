# website/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .models import Product
from .forms import SignUpForm, ProductForm
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
import io


# ─── Helper de roles ──────────────────────────────────────────────────────────

def is_admin(user):
    """
    Patrón: Facade — encapsula la lógica de verificación de rol.
    Retorna True si el usuario es superusuario, staff, o miembro del grupo 'Administrador'.
    """
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name='Administrador').exists()
    )


# ─── Vistas principales ───────────────────────────────────────────────────────

def home(request):
    """
    Punto de entrada principal.
    - Si el usuario es Admin → redirige al dashboard de administrador.
    - Si es Operador → muestra SOLO sus propios productos.
    - Si no está autenticado → muestra la pantalla de login.
    """
    if request.method == 'POST' and 'action' not in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "¡Sesión iniciada correctamente!")
            # Redirigir según rol
            if is_admin(user):
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, "¡Credenciales inválidas!")
            return redirect('home')
    else:
        if request.user.is_authenticated:
            # Admins no deben estar aquí
            if is_admin(request.user):
                return redirect('admin_dashboard')

            # ── Dashboard del Operador: solo SUS productos ──────────────────
            products = Product.objects.filter(user=request.user).order_by('-created_at')
            total_products  = products.count()
            total_units     = products.aggregate(total=Sum('quantity'))['total'] or 0
            total_categories = products.values('category').distinct().count()

            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_count   = products.filter(created_at__gte=seven_days_ago).count()
            low_stock      = products.filter(quantity__lte=5).order_by('quantity')
            top_stock      = products.order_by('-quantity')[:5]
            recent_activity = products.order_by('-created_at')[:10]

            by_category = (
                products.values('category')
                .annotate(count=Count('id'), total_qty=Sum('quantity'))
                .order_by('-total_qty')
            )

            chart_labels = [item['category'] for item in by_category]
            chart_data   = [item['total_qty'] for item in by_category]
            chart_counts = [item['count'] for item in by_category]

            context = {
                'products':        products,
                'total_products':  total_products,
                'total_categories': total_categories,
                'user_is_admin':   False,
                'total_units':     total_units,
                'by_category':     by_category,
                'by_user':         [],
                'recent_count':    recent_count,
                'low_stock':       low_stock,
                'top_stock':       top_stock,
                'recent_activity': recent_activity,
                'chart_labels':    chart_labels,
                'chart_data':      chart_data,
                'chart_counts':    chart_counts,
                'product_form':    ProductForm(),
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
        if is_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ── Patrón Observer: asignar rol Operador automáticamente ──────
            try:
                op_group = Group.objects.get(name='Operador')
                user.groups.add(op_group)
            except Group.DoesNotExist:
                pass

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


# ─── Dashboard de Administrador ───────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    """
    Dashboard exclusivo para Administradores.
    Muestra todos los productos, estadísticas globales y gestión de usuarios.
    Redirige a home si el usuario no es admin (403 implícito).
    """
    if not is_admin(request.user):
        messages.error(request, "⛔ Acceso denegado. No tienes permisos de Administrador.")
        return redirect('home')

    # ── Todos los productos del sistema ──────────────────────────────────────
    products = Product.objects.select_related('user').all().order_by('-created_at')
    total_products   = products.count()
    total_units      = products.aggregate(total=Sum('quantity'))['total'] or 0
    total_categories = products.values('category').distinct().count()

    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_count   = products.filter(created_at__gte=seven_days_ago).count()
    low_stock      = products.filter(quantity__lte=5).order_by('quantity')
    top_stock      = products.order_by('-quantity')[:5]
    recent_activity = products.order_by('-created_at')[:10]

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

    chart_labels = [item['category'] for item in by_category]
    chart_data   = [item['total_qty'] for item in by_category]
    chart_counts = [item['count'] for item in by_category]

    # ── Gestión de usuarios ───────────────────────────────────────────────────
    admin_group = Group.objects.filter(name='Administrador').first()
    all_users   = User.objects.prefetch_related('groups').order_by('username')

    users_info = []
    for u in all_users:
        users_info.append({
            'user':     u,
            'is_admin': (
                u.is_superuser
                or u.is_staff
                or (admin_group and u.groups.filter(pk=admin_group.pk).exists())
            ),
            'product_count': Product.objects.filter(user=u).count(),
        })

    context = {
        'products':         products,
        'total_products':   total_products,
        'total_categories': total_categories,
        'total_units':      total_units,
        'total_users':      all_users.count(),
        'recent_count':     recent_count,
        'low_stock':        low_stock,
        'top_stock':        top_stock,
        'recent_activity':  recent_activity,
        'by_category':      by_category,
        'by_user':          by_user,
        'chart_labels':     chart_labels,
        'chart_data':       chart_data,
        'chart_counts':     chart_counts,
        'users_info':       users_info,
        'product_form':     ProductForm(),
        'user_is_admin':    True,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def promote_user(request, pk):
    """
    Permite al Administrador promover o degradar el rol de un usuario.
    POST alterna entre Administrador y Operador.
    """
    if not is_admin(request.user):
        messages.error(request, "⛔ Acceso denegado.")
        return redirect('home')

    target_user = get_object_or_404(User, pk=pk)

    # No permitir que un admin se quite sus propios permisos
    if target_user == request.user:
        messages.warning(request, "No puedes cambiar tu propio rol.")
        return redirect('admin_dashboard')

    # No modificar superusuarios
    if target_user.is_superuser:
        messages.warning(request, f"No se puede modificar al superusuario '{target_user.username}'.")
        return redirect('admin_dashboard')

    admin_group    = get_object_or_404(Group, name='Administrador')
    operator_group = Group.objects.filter(name='Operador').first()

    if target_user.groups.filter(name='Administrador').exists():
        # Degradar a Operador
        target_user.groups.remove(admin_group)
        if operator_group:
            target_user.groups.add(operator_group)
        messages.success(request, f"✅ '{target_user.username}' ahora es Operador.")
    else:
        # Promover a Administrador
        if operator_group:
            target_user.groups.remove(operator_group)
        target_user.groups.add(admin_group)
        messages.success(request, f"👑 '{target_user.username}' ahora es Administrador.")

    return redirect('admin_dashboard')


# ─── CRUD de Productos ────────────────────────────────────────────────────────

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product      = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, f"Producto '{product.name}' registrado correctamente.")
        else:
            errores = []
            for field, error_list in form.errors.items():
                for error in error_list:
                    errores.append(error)
            messages.error(request, "Error de validación: " + " | ".join(errores))

    if is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('home')


@login_required
def delete_product(request, pk):
    """
    Elimina un producto.
    - Administradores pueden eliminar CUALQUIER producto.
    - Operadores solo pueden eliminar sus PROPIOS productos.
    """
    if is_admin(request.user):
        product = get_object_or_404(Product, pk=pk)
    else:
        product = get_object_or_404(Product, pk=pk, user=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, f"El producto '{product.name}' ha sido eliminado.")

    if is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('home')


@login_required
def edit_product(request, pk):
    """
    Edita un producto.
    - Administradores pueden editar CUALQUIER producto.
    - Operadores solo pueden editar sus PROPIOS productos.
    """
    if is_admin(request.user):
        product = get_object_or_404(Product, pk=pk)
    else:
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

    if is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('home')


@login_required
def reportes(request):
    """Vista de reportes — redirige al dashboard correspondiente."""
    if is_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('home')


# ─── Exportaciones ────────────────────────────────────────────────────────────

@login_required
def export_csv(request):
    """
    Exportar inventario como CSV compatible con Excel (BOM UTF-8).
    Admins exportan todo; Operadores exportan solo sus productos.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="inventario_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    response.write('\ufeff')  # BOM para compatibilidad con Excel

    writer = csv.writer(response)
    writer.writerow(['Producto', 'Categoría', 'Cantidad', 'Registrado por', 'Fecha de Registro'])

    if is_admin(request.user):
        products = Product.objects.all().order_by('-created_at')
    else:
        products = Product.objects.filter(user=request.user).order_by('-created_at')

    for p in products:
        writer.writerow([
            p.name,
            p.category,
            p.quantity,
            p.user.username,
            p.created_at.strftime('%d/%m/%Y %H:%M'),
        ])

    return response


@login_required
def export_pdf(request):
    """
    Exportar inventario como PDF usando ReportLab.
    Admins exportan todo; Operadores exportan solo sus productos.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm,   bottomMargin=2 * cm,
        title='Reporte de Inventario',
        author='Sistema de Inventario DCRM',
    )

    styles = getSampleStyleSheet()
    elements = []

    color_primary   = colors.HexColor('#6366f1')
    color_secondary = colors.HexColor('#64748b')
    color_header_bg = colors.HexColor('#1e293b')
    color_row_alt   = colors.HexColor('#f8fafc')
    color_danger    = colors.HexColor('#ef4444')
    color_warning   = colors.HexColor('#f59e0b')

    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=color_primary,
        alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', fontSize=10, textColor=color_secondary,
        alignment=TA_CENTER, spaceAfter=20,
    )
    section_style = ParagraphStyle(
        'SectionTitle', fontSize=11, textColor=color_header_bg,
        fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6,
    )
    footer_style = ParagraphStyle(
        'Footer', fontSize=8, textColor=color_secondary, alignment=TA_CENTER,
    )

    role_label = 'Administrador' if is_admin(request.user) else 'Operador'
    elements.append(Paragraph('📦 Reporte de Inventario', title_style))
    elements.append(Paragraph(
        f'Generado el {timezone.now().strftime("%d/%m/%Y a las %H:%M")} '
        f'por {request.user.get_full_name() or request.user.username} ({role_label})',
        subtitle_style
    ))
    elements.append(HRFlowable(width='100%', thickness=2, color=color_primary, spaceAfter=16))

    if is_admin(request.user):
        products = Product.objects.all().order_by('-created_at')
    else:
        products = Product.objects.filter(user=request.user).order_by('-created_at')

    total_units = products.aggregate(total=Sum('quantity'))['total'] or 0
    total_cats  = products.values('category').distinct().count()
    low_count   = products.filter(quantity__lte=5).count()

    summary_data = [
        ['Total Productos', 'Unidades Totales', 'Categorías', 'Stock Bajo (≤5)'],
        [str(products.count()), str(total_units), str(total_cats), str(low_count)],
    ]
    summary_table = Table(summary_data, colWidths=[4.3 * cm] * 4)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), color_header_bg),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 9),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME',     (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 1), (-1, 1), 16),
        ('TEXTCOLOR',    (0, 1), (0,  1), color_primary),
        ('TEXTCOLOR',    (1, 1), (1,  1), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR',    (2, 1), (2,  1), color_warning),
        ('TEXTCOLOR',    (3, 1), (3,  1), color_danger),
        ('ROWBACKGROUNDS', (0, 1), (-1, 1), [colors.white]),
        ('BOX',          (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID',    (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph('Listado Completo de Productos', section_style))
    table_data = [['#', 'Producto', 'Categoría', 'Cantidad', 'Registrado por', 'Fecha']]
    for i, p in enumerate(products, 1):
        table_data.append([
            str(i), p.name, p.category, str(p.quantity),
            p.user.username, p.created_at.strftime('%d/%m/%Y'),
        ])

    col_widths = [1 * cm, 5 * cm, 3.8 * cm, 2.2 * cm, 3 * cm, 2.5 * cm]
    inv_table  = Table(table_data, colWidths=col_widths, repeatRows=1)

    row_count = len(table_data)
    table_styles = [
        ('BACKGROUND',   (0, 0), (-1, 0), color_primary),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 9),
        ('ALIGN',        (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME',     (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1), 8),
        ('ALIGN',        (0, 1), (-1, -1), 'CENTER'),
        ('ALIGN',        (1, 1), (2, -1), 'LEFT'),
        ('BOX',          (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID',    (0, 0), (-1, -1), 0.25, colors.HexColor('#e2e8f0')),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]
    for row_i in range(1, row_count):
        p = products[row_i - 1]
        bg = color_row_alt if row_i % 2 == 0 else colors.white
        table_styles.append(('BACKGROUND', (0, row_i), (-1, row_i), bg))
        if p.quantity == 0:
            table_styles.append(('TEXTCOLOR', (3, row_i), (3, row_i), color_danger))
            table_styles.append(('FONTNAME',  (3, row_i), (3, row_i), 'Helvetica-Bold'))
        elif p.quantity <= 5:
            table_styles.append(('TEXTCOLOR', (3, row_i), (3, row_i), color_warning))
            table_styles.append(('FONTNAME',  (3, row_i), (3, row_i), 'Helvetica-Bold'))

    inv_table.setStyle(TableStyle(table_styles))
    elements.append(inv_table)
    elements.append(Spacer(1, 0.8 * cm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        f'Sistema de Inventario DCRM  ·  {timezone.now().strftime("%d/%m/%Y %H:%M")}',
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="inventario_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    )
    return response