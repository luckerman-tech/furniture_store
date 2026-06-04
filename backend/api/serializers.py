from rest_framework import serializers
from django.db.models import Sum
from .models import *

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'

class AssortmentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    style_name = serializers.CharField(source='style.name', read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Assortment
        fields = ['id', 'name', 'price', 'category', 'category_name', 'style', 'style_name', 'total_quantity']

class KitSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Kit
        fields = '__all__'

class KitItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitItem
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=4)
    
    class Meta:
        model = Client
        fields = ['id', 'full_name', 'address', 'login', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        client = Client(**validated_data)
        client.set_password(password)
        client.save()
        return client

class OrderStatusSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'client_name', 'datetime', 'status', 'items_count']
    
    def get_items_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'client_name', 'datetime', 'status', 'items']
    
    def get_items(self, obj):
        items_data = []
        for item in obj.items.all():
            if item.assortment:
                items_data.append({
                    'type': 'product',
                    'id': item.id,
                    'product_id': item.assortment.id,
                    'product_name': item.assortment.name,
                    'price': float(item.assortment.price),
                    'quantity': item.quantity,
                    'total': float(item.assortment.price * item.quantity)
                })
            elif item.kit:
                items_data.append({
                    'type': 'kit',
                    'id': item.id,
                    'kit_id': item.kit.id,
                    'kit_name': item.kit.name,
                    'quantity': item.quantity
                })
        return items_data

class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'client_name', 'datetime', 'status', 'items_count', 'total_quantity']
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_total_quantity(self, obj):
        total = obj.items.aggregate(total=Sum('quantity'))['total']
        return total or 0

    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'assortment', 'kit', 'quantity']
        extra_kwargs = {
            'order': {'required': True},
            'quantity': {'min_value': 1}
        }

class ParishSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    assortment_name = serializers.CharField(source='assortment.name', read_only=True)
    
    class Meta:
        model = Parish
        fields = ['id', 'warehouse', 'warehouse_name', 'assortment', 'assortment_name', 
                  'quantity', 'datetime', 'created_by']

class StorageSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    assortment_name = serializers.CharField(source='assortment.name', read_only=True)
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Storage
        fields = ['id', 'warehouse', 'warehouse_name', 'assortment', 'assortment_name', 
                  'quantity', 'total_value']
    
    def get_total_value(self, obj):
        return float(obj.quantity * obj.assortment.price) if obj.assortment else 0

class ExpenseSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    assortment_name = serializers.CharField(source='assortment.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'warehouse', 'warehouse_name', 'assortment', 'assortment_name', 
                  'quantity', 'datetime', 'created_by']