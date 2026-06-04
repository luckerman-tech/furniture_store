from django.contrib import admin
from .models import Category, Style, Warehouse, Assortment, Kit, Client, Order, KitItem, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Assortment)
class AssortmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'style')
    list_filter = ('category', 'style')
    search_fields = ('name',)

@admin.register(Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(KitItem)
class KitItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'kit', 'assortment', 'quantity', 'discount_percent')
    list_filter = ('kit', 'assortment')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'login', 'address')
    search_fields = ('full_name', 'login')
    readonly_fields = ('password',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'datetime')
    list_filter = ('datetime',)
    filter_horizontal = ()

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'assortment', 'kit', 'quantity')
