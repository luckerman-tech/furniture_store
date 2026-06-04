"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from datetime import datetime

class Warehouse(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Warehouses'

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Categories'

class Style(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Styles'

class Assortment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators = [MinValueValidator(0.01, 'Цена должна быть положительным числом')])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Assortment'
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name='price_positive'
            )
        ]
    
    def save(self, *args, **kwargs):
        if self.price <= 0:
            raise ValidationError({'price': 'Цена должна быть больше 0'})
        super().save(*args, **kwargs)

class Parish(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_storage()
    
    def update_storage(self):
        storage, created = Storage.objects.get_or_create(
            warehouse=self.warehouse,
            assortment=self.assortment,
            defaults={'quantity': 0}
        )
        storage.quantity += self.quantity
        storage.save()
    
    class Meta:
        db_table = 'Parishes'

class Storage(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'Storage'
        unique_together = ['warehouse', 'assortment']

class Expense(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'Expenses'

class Kit(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Kits'

class KitItem(models.Model):
    kit = models.ForeignKey(Kit, on_delete=models.CASCADE, related_name='items')
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators = [MinValueValidator(0, 'Процент скидки должен быть неотрицательным числом')])
    
    class Meta:
        db_table = 'KitItems'

class Client(models.Model):
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name
    
    class Meta:
        db_table = 'Clients'

class OrderStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    CONFIRMED = 'confirmed', 'Подтвержден'
    PROCESSING = 'processing', 'В обработке'
    SHIPPED = 'shipped', 'Отправлен'
    DELIVERED = 'delivered', 'Доставлен'
    CANCELLED = 'cancelled', 'Отменен'

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW)
    
    def __str__(self):
        return f"Заказ №{self.id} от {self.client}"

    class Meta:
        db_table = 'Orders'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    assortment = models.ForeignKey(Assortment, on_delete=models.CASCADE, null=True, blank=True)
    kit = models.ForeignKey(Kit, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    
    def __str__(self):
        if self.assortment:
            return f"{self.order.id} - {self.assortment.name} x{self.quantity}"
        elif self.kit:
            return f"{self.order.id} - {self.kit.name} x{self.quantity}"
        return f"{self.order.id} - item {self.id}"
    
    class Meta:
        db_table = 'OrderItems'
