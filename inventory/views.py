import csv
import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from inventory.forms import (
    UserRegistry, ProductForm, OrderForm, UserUpdateForm,
    UserProfileForm, SupplierForm,
)
from inventory.models import Product, Order, UserProfile, Supplier, ActivityLog


def _log(user, action, description):
    ActivityLog.objects.create(user=user, action=action, description=description)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@login_required
def index(request):
    products = Product.objects.all()
    orders_qs = Order.objects.all()
    users = User.objects.all()

    total_products = products.count()
    total_orders = orders_qs.count()
    total_users = users.count()
    total_suppliers = Supplier.objects.count()

    low_stock = products.filter(quantity__lte=10)

    if request.user.is_staff and request.user.is_superuser:
        recent_orders = orders_qs.order_by('-date')[:5]
    else:
        recent_orders = orders_qs.filter(created_by=request.user).order_by('-date')[:5]

    categories = {}
    for product in products:
        cat = product.category or 'Uncategorized'
        categories[cat] = categories.get(cat, 0) + 1

    order_statuses = {}
    for order in orders_qs:
        status = order.status or 'Pending'
        order_statuses[status] = order_statuses.get(status, 0) + 1

    recent_activity = ActivityLog.objects.all()[:8]

    context = {
        'title': 'Dashboard',
        'orders': recent_orders,
        'users': users.order_by('-date_joined')[:5],
        'products': products[:5],
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_suppliers': total_suppliers,
        'low_stock': low_stock,
        'low_stock_count': low_stock.count(),
        'category_labels': json.dumps(list(categories.keys())),
        'category_data': json.dumps(list(categories.values())),
        'status_labels': json.dumps(list(order_statuses.keys())),
        'status_data': json.dumps(list(order_statuses.values())),
        'recent_activity': recent_activity,
    }
    return render(request, 'index.html', context)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
@login_required
def products(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    all_products = Product.objects.select_related('supplier').order_by('name')

    if query:
        all_products = all_products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category:
        all_products = all_products.filter(category=category)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            _log(request.user, 'PRODUCT_ADDED', f'Added product "{product.name}" (qty: {product.quantity})')
            messages.success(request, 'Product added successfully!')
            return redirect('products')
    else:
        form = ProductForm()

    paginator = Paginator(all_products, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Products',
        'products': page_obj,
        'form': form,
        'query': query,
        'selected_category': category,
        'page_obj': page_obj,
    }
    return render(request, 'products.html', context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('supplier'), pk=pk)
    product_orders = Order.objects.filter(product=product).order_by('-date')

    total_ordered = product_orders.aggregate(total=Sum('order_quantity'))['total'] or 0

    context = {
        'title': 'Product Detail',
        'product': product,
        'orders': product_orders,
        'total_ordered': total_ordered,
    }
    return render(request, 'product_detail.html', context)


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            _log(request.user, 'PRODUCT_UPDATED', f'Updated product "{product.name}"')
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products')
    else:
        form = ProductForm(instance=product)

    context = {
        'title': 'Edit Product',
        'form': form,
        'product': product,
    }
    return render(request, 'product_edit.html', context)


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        _log(request.user, 'PRODUCT_DELETED', f'Deleted product "{name}"')
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('products')
    context = {
        'title': 'Delete Product',
        'product': product,
    }
    return render(request, 'product_delete.html', context)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
@login_required
def orders(request):
    if request.user.is_staff and request.user.is_superuser:
        all_orders = Order.objects.select_related('product', 'created_by').all().order_by('-date')
    else:
        all_orders = Order.objects.select_related('product', 'created_by').filter(
            created_by=request.user
        ).order_by('-date')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            _log(request.user, 'ORDER_CREATED',
                 f'Created order for "{instance.product}" (qty: {instance.order_quantity})')
            messages.success(request, 'Order created successfully!')
            return redirect('orders')
    else:
        form = OrderForm()

    paginator = Paginator(all_orders, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Orders',
        'orders': page_obj,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'orders.html', context)


@login_required
def order_update_status(request, pk):
    """Admin-only inline status change with automatic stock adjustment."""
    if not (request.user.is_staff and request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect('orders')

    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status', '')

    if new_status not in dict(Order._meta.get_field('status').choices):
        messages.error(request, 'Invalid status.')
        return redirect('orders')

    old_status = order.status
    product = order.product

    if old_status == new_status:
        return redirect('orders')

    # Stock adjustment logic
    if new_status == 'Approved' and old_status != 'Approved':
        if product and product.quantity is not None and product.quantity >= order.order_quantity:
            product.quantity -= order.order_quantity
            product.save()
            _log(request.user, 'STOCK_ADJUSTED',
                 f'Stock for "{product.name}" decreased by {order.order_quantity} (now {product.quantity})')
        elif product:
            messages.error(
                request,
                f'Insufficient stock for "{product.name}". Available: {product.quantity}, Requested: {order.order_quantity}'
            )
            return redirect('orders')

    elif old_status == 'Approved' and new_status in ('Cancelled', 'Pending'):
        if product:
            product.quantity = (product.quantity or 0) + order.order_quantity
            product.save()
            _log(request.user, 'STOCK_ADJUSTED',
                 f'Stock for "{product.name}" restored by {order.order_quantity} (now {product.quantity})')

    order.status = new_status
    order.save()
    _log(request.user, 'ORDER_STATUS',
         f'Order #{order.pk} status: {old_status} → {new_status}')
    messages.success(request, f'Order status updated to {new_status}.')
    return redirect('orders')


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        desc = f'Deleted order for "{order.product}" (qty: {order.order_quantity})'
        if order.status == 'Approved' and order.product:
            order.product.quantity = (order.product.quantity or 0) + order.order_quantity
            order.product.save()
            _log(request.user, 'STOCK_ADJUSTED',
                 f'Stock for "{order.product.name}" restored by {order.order_quantity}')
        order.delete()
        _log(request.user, 'ORDER_DELETED', desc)
        messages.success(request, 'Order deleted successfully!')
        return redirect('orders')
    context = {
        'title': 'Delete Order',
        'order': order,
    }
    return render(request, 'order_delete.html', context)


# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------
@login_required
def suppliers(request):
    query = request.GET.get('q', '')
    all_suppliers = Supplier.objects.all()

    if query:
        all_suppliers = all_suppliers.filter(
            Q(name__icontains=query) | Q(contact_person__icontains=query) | Q(email__icontains=query)
        )

    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            _log(request.user, 'SUPPLIER_ADDED', f'Added supplier "{supplier.name}"')
            messages.success(request, 'Supplier added successfully!')
            return redirect('suppliers')
    else:
        form = SupplierForm()

    paginator = Paginator(all_suppliers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Suppliers',
        'suppliers': page_obj,
        'form': form,
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'suppliers.html', context)


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            _log(request.user, 'SUPPLIER_UPDATED', f'Updated supplier "{supplier.name}"')
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('suppliers')
    else:
        form = SupplierForm(instance=supplier)

    context = {
        'title': 'Edit Supplier',
        'form': form,
        'supplier': supplier,
    }
    return render(request, 'supplier_edit.html', context)


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        _log(request.user, 'SUPPLIER_DELETED', f'Deleted supplier "{name}"')
        messages.success(request, f'Supplier "{name}" deleted successfully!')
        return redirect('suppliers')
    context = {
        'title': 'Delete Supplier',
        'supplier': supplier,
    }
    return render(request, 'supplier_delete.html', context)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
@login_required
def users(request):
    all_users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(all_users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Users',
        'users': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'users.html', context)


# ---------------------------------------------------------------------------
# Profile & Password
# ---------------------------------------------------------------------------
@login_required
def user(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'title': 'Profile',
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'user.html', context)


@login_required
def password_change(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user_obj = form.save()
            update_session_auth_hash(request, user_obj)
            messages.success(request, 'Password changed successfully!')
            return redirect('user')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'title': 'Change Password',
        'form': form,
    }
    return render(request, 'password_change.html', context)


# ---------------------------------------------------------------------------
# Activity Log
# ---------------------------------------------------------------------------
@login_required
def activity_log(request):
    logs = ActivityLog.objects.select_related('user').all()
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Activity Log',
        'logs': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'activity_log.html', context)


# ---------------------------------------------------------------------------
# CSV Exports
# ---------------------------------------------------------------------------
@login_required
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Quantity', 'Description', 'Supplier'])

    for p in Product.objects.select_related('supplier').all():
        writer.writerow([
            p.name, p.category, p.quantity, p.description,
            p.supplier.name if p.supplier else '-'
        ])

    return response


@login_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product', 'Ordered By', 'Quantity', 'Status', 'Date'])

    qs = Order.objects.select_related('product', 'created_by').all().order_by('-date')
    if not (request.user.is_staff and request.user.is_superuser):
        qs = qs.filter(created_by=request.user)

    for o in qs:
        writer.writerow([
            o.product, o.created_by.get_full_name() or o.created_by.username,
            o.order_quantity, o.status, o.date.strftime('%Y-%m-%d %H:%M')
        ])

    return response


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register(request):
    if request.method == 'POST':
        form = UserRegistry(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = UserRegistry()

    context = {
        'title': 'Register',
        'form': form,
    }
    return render(request, 'register.html', context)
