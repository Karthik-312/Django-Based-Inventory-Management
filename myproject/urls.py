from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='dash'),

    # Products
    path('products/', views.products, name='products'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product-edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product-delete'),
    path('products/export/', views.export_products_csv, name='export-products'),

    # Orders
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order-delete'),
    path('orders/<int:pk>/status/', views.order_update_status, name='order-update-status'),
    path('orders/export/', views.export_orders_csv, name='export-orders'),

    # Suppliers
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier-edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier-delete'),

    # Users & Profile
    path('users/', views.users, name='users'),
    path('user/', views.user, name='user'),
    path('password/', views.password_change, name='password-change'),

    # Activity Log
    path('activity/', views.activity_log, name='activity-log'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth.LogoutView.as_view(template_name='logout.html'), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
