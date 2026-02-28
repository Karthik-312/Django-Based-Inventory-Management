from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CATEGORY = (
    ('Stationary', 'Stationary'),
    ('Electronics', 'Electronics'),
    ('Food', 'Food'),
    ('Sports', 'Sports'),
)

ORDER_STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    physical_address = models.CharField(max_length=40, null=True, blank=True)
    mobile = models.CharField(max_length=12, null=True, blank=True)
    picture = models.ImageField(default='avatar.jpeg', upload_to='Pictures')

    def __str__(self):
        return self.user.username


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY, null=True)
    quantity = models.PositiveIntegerField(null=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products'
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product} ordered quantity {self.order_quantity}'


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('PRODUCT_ADDED', 'Product Added'),
        ('PRODUCT_UPDATED', 'Product Updated'),
        ('PRODUCT_DELETED', 'Product Deleted'),
        ('ORDER_CREATED', 'Order Created'),
        ('ORDER_STATUS', 'Order Status Changed'),
        ('ORDER_DELETED', 'Order Deleted'),
        ('SUPPLIER_ADDED', 'Supplier Added'),
        ('SUPPLIER_UPDATED', 'Supplier Updated'),
        ('SUPPLIER_DELETED', 'Supplier Deleted'),
        ('STOCK_ADJUSTED', 'Stock Adjusted'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user} - {self.get_action_display()}'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
