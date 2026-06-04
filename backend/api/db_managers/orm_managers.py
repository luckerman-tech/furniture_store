from django.db.models import Q, F, Sum, Count, Avg
from ..models import *
from decimal import Decimal

class ORMWarehouseManager:
    @staticmethod
    def get_all():
        return Warehouse.objects.all()
    
    @staticmethod
    def create(name):
        return Warehouse.objects.create(name=name)
    
    @staticmethod
    def update(warehouse_id, name):
        return Warehouse.objects.filter(id=warehouse_id).update(name=name)
    
    @staticmethod
    def delete(warehouse_id):
        return Warehouse.objects.filter(id=warehouse_id).delete()[0] > 0

class ORMAssortmentManager:
    @staticmethod
    def get_all():
        return Assortment.objects.select_related('category', 'style').all()

    @staticmethod
    def search_by_name(keyword):
        return Assortment.objects.filter(name__icontains=keyword)
    
    @staticmethod
    def filter_by_category(category_id):
        return Assortment.objects.filter(category_id=category_id).select_related('category', 'style')
    
    @staticmethod
    def filter_by_style(style_id):
        return Assortment.objects.filter(style_id=style_id).select_related('category', 'style')
    
    @staticmethod
    def filter_by_price_range(min_price, max_price):
        return Assortment.objects.filter(price__gte=min_price, price__lte=max_price)

    @staticmethod
    def filter_combined(name=None, category_id=None, style_id=None, min_price=None, max_price=None):
        queryset = Assortment.objects.select_related('category', 'style').all()
        
        if name and name != '':
            queryset = queryset.filter(name__icontains=name)

        if category_id and category_id != '0':
            queryset = queryset.filter(category_id=category_id)

        if style_id and style_id != '0':
            queryset = queryset.filter(style_id=style_id)
        
        if min_price and min_price != '0':
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price and max_price != '999999':
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        return queryset
    
    @staticmethod
    def create(name, price, category_id, style_id):
        return Assortment.objects.create(
            name=name, price=price,
            category_id=category_id, style_id=style_id
        )
    
    @staticmethod
    def update(assortment_id, **kwargs):
        return Assortment.objects.filter(id=assortment_id).update(**kwargs)
    
    @staticmethod
    def delete(assortment_id):
        return Assortment.objects.filter(id=assortment_id).delete()[0] > 0

class ORMOrderManager:
    @staticmethod
    def get_client_orders(client_id):
        return Order.objects.filter(client_id=client_id).prefetch_related('items')
    
    @staticmethod
    def create_order(client_id):
        return Order.objects.create(client_id=client_id)
    
    @staticmethod
    def get_order_total(order_id):
        order_items = OrderItem.objects.filter(order_id=order_id)
        total = Decimal('0')
        
        for item in order_items:
            if item.assortment:
                total += item.assortment.price * item.quantity
            elif item.kit:
                kit_total = Decimal('0')
                for kit_item in item.kit.items.all():
                    discounted_price = kit_item.assortment.price * (1 - kit_item.discount_percent / 100)
                    kit_total += discounted_price * kit_item.quantity
                total += kit_total * item.quantity
        
        return total

class ORMReportManager:
    @staticmethod
    def get_top_products(limit=10):
        return Assortment.objects.annotate(
            total_quantity=Sum('orderitem__quantity')
        ).filter(
            total_quantity__gt=0
        ).order_by('-total_quantity').values(
            'id', 'name', 'price', 'total_quantity'
        )[:limit]
    
    @staticmethod
    def get_category_stats():
        return Category.objects.annotate(
            total_products=Count('assortment'),
            avg_price=Avg('assortment__price')
        )
    
    @staticmethod
    def get_storage_value():
        return Storage.objects.filter(quantity__gt=0).aggregate(
            total_value=Sum(F('quantity') * F('assortment__price'))
        )
