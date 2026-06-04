"""
Definition of views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from .models import *
from .serializers import *
from .db_managers.sql_managers import *
from .db_managers.orm_managers import *
from .services.order_processing_service import OrderProcessingService
from .permissions import IsAdminUser

class AuthView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        login = request.data.get('login')
        password = request.data.get('password')
        
        try:
            client = Client.objects.get(login=login)
            if client.check_password(password):
                user, created = User.objects.get_or_create(
                    username=login,
                    defaults={
                        'first_name': client.full_name.split()[0] if client.full_name else '',
                        'last_name': client.full_name.split()[-1] if len(client.full_name.split()) > 1 else '',
                    }
                )

                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'client_id': client.id,
                    'full_name': client.full_name
                })
        except Client.DoesNotExist:
            pass
        except Exception as e:
            print(f"Auth error: {e}")
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            password = request.data.get('password')
            client = serializer.save()
            client.set_password(password)
            client.save()
            
            return Response({
                'id': client.id,
                'full_name': client.full_name,
                'login': client.login,
                'message': 'Регистрация успешна'
            }, status=status.HTTP_201_CREATED)
        
        print("Ошибки валидации:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssortmentViewSet(viewsets.ModelViewSet):
    queryset = Assortment.objects.all()
    serializer_class = AssortmentSerializer
    
    @action(detail=False, methods=['get'])
    def using_sql(self, request):
        name = request.query_params.get('name')
        category_id = request.query_params.get('category_id')
        style_id = request.query_params.get('style_id')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
    
        items = SQLAssortmentManager.filter_combined(
            name = name,
            category_id=category_id,
            style_id = style_id,
            min_price=min_price,
            max_price=max_price
        )
    
        return Response({'items': items})
    
    @action(detail=False, methods=['get'])
    def using_orm(self, request):
        name = request.query_params.get('name')
        category_id = request.query_params.get('category_id')
        style_id = request.query_params.get('style_id')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
    
        items = ORMAssortmentManager.filter_combined(
            name = name,
            category_id=category_id,
            style_id = style_id,
            min_price=min_price,
            max_price=max_price
        )
    
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def using_sql_create(self, request):
        name = request.data.get('name')
        price = request.data.get('price')
        category_id = request.data.get('category_id')
        style_id = request.data.get('style_id')
    
        if not all([name, price, category_id, style_id]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        try:
            from .db_managers.sql_managers import SQLAssortmentManager
            product_id = SQLAssortmentManager.create(
                name=name,
                price=price,
                category_id=category_id,
                style_id=style_id
            )
        
            return Response(
                {'id': product_id, 'message': 'Product created successfully'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-datetime')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer

    @action(detail=True, methods=['get'])
    def calculate_total(self, request, pk=None):
        try:
            order = self.get_object()
            total = 0
            
            for item in order.items.all():
                if item.assortment:
                    total += item.assortment.price * item.quantity
                elif item.kit:
                    for kit_item in item.kit.items.all():
                        discounted_price = kit_item.assortment.price * (1 - kit_item.discount_percent / 100)
                        total += discounted_price * kit_item.quantity * item.quantity
            
            return Response({
                'order_id': order.id,
                'total': float(total),
                'message': 'Total calculated'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def calculate_with_discount(self, request, pk=None):
        try:
            order = self.get_object()
            
            client = order.client
            order_count = Order.objects.filter(client=client).count()
            
            from .services.discount_strategy import ClientLoyaltyStrategy, KitDiscountStrategy
            
            has_kits = order.items.filter(kit__isnull=False).exists()
            
            if has_kits:
                strategy = KitDiscountStrategy()
            else:
                strategy = ClientLoyaltyStrategy(order_count)
            
            from .services.order_service import OrderService
            order_service = OrderService(strategy)
            final_price = order_service.calculate_final_price(pk)
            
            return Response({
                'order_id': order.id,
                'final_price': float(final_price),
                'discount_applied': True
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def reports_sql(self, request):
        report_type = request.query_params.get('type', 'storage')
        
        if report_type == 'storage':
            data = SQLStorageReportManager.get_storage_report()
        elif report_type == 'movement':
            product_id = request.query_params.get('product_id')
            data = SQLStorageReportManager.get_product_movement(product_id)
        else:
            data = []
        
        return Response({'report': data})
    
    @action(detail=False, methods=['get'])
    def reports_orm(self, request):
        report_type = request.query_params.get('type', 'top_products')
        
        if report_type == 'top_products':
            data = ORMReportManager.get_top_products()
            return Response({'report': data})
        elif report_type == 'category_stats':
            data = ORMReportManager.get_category_stats()
            return Response({'report': [
                {'category': cat.name, 'total_products': cat.total_products, 'avg_price': cat.avg_price}
                for cat in data
            ]})
        elif report_type == 'storage_value':
            data = ORMReportManager.get_storage_value()
            return Response({'report': data})
        
        return Response({'error': 'Invalid report type'})
    
    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        warehouse_id = request.query_params.get('warehouse_id')
        
        result = OrderProcessingService.check_availability(pk, warehouse_id)
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def get_picklist(self, request, pk=None):
        picklist = OrderProcessingService.get_order_picklist(pk)
        return Response({'picklist': picklist})
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        warehouse_items = request.data.get('warehouse_items')
        if not warehouse_items:
            return Response(
                {'error': 'Не указаны склады для списания'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = OrderProcessingService.process_order(pk, warehouse_items)
        if result['status'] == 'success':
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order = self.get_object()
            if order.status == 'cancelled':
                return Response({'error': 'Заказ уже отменен'}, status=400)
            
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'cancelled', 'order_id': order.id})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in ['new', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']:
            return Response({'error': 'Неверный статус'}, status=400)
        
        order = self.get_object()
        order.status = new_status
        order.save()
        return Response({'status': order.status, 'order_id': order.id})

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
    @action(detail=False, methods=['post'])
    def create_sql(self, request):
        name = request.data.get('name')
        warehouse_id = SQLWarehouseManager.create(name)
        return Response({'id': warehouse_id})
    
    @action(detail=False, methods=['post'])
    def create_orm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class KitViewSet(viewsets.ModelViewSet):
    queryset = Kit.objects.all()
    serializer_class = KitSerializer
    
    @action(detail=True, methods=['get'])
    def calculate_discount(self, request, pk=None):
        kit = self.get_object()
        total = Decimal('0')
        
        for item in kit.items.all():
            item_total = item.assortment.price * item.quantity
            discount = item_total * (item.discount_percent / 100)
            total += item_total - discount
        
        return Response({
            'kit_id': pk,
            'kit_name': kit.name,
            'total_with_discount': total
        })

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name']
    
    @action(detail=False, methods=['get'])
    def using_sql(self, request):
        from .db_managers.sql_managers import SQLCategoryManager
        categories = SQLCategoryManager.get_all()
        return Response({'categories': categories})
    
    @action(detail=False, methods=['get'])
    def using_orm(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer
    search_fields = ['name']
    
    @action(detail=False, methods=['get'])
    def using_sql(self, request):
        from .db_managers.sql_managers import SQLStyleManager
        styles = SQLStyleManager.get_all()
        return Response({'styles': styles})
    
    @action(detail=False, methods=['get'])
    def using_orm(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(f"OrderItem create errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        order_id = request.query_params.get('order_id')
        if order_id:
            items = OrderItem.objects.filter(order_id=order_id)
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data)
        return Response({'error': 'order_id required'}, status=400)

class ParishViewSet(viewsets.ModelViewSet):
    queryset = Parish.objects.all().order_by('-datetime')
    serializer_class = ParishSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.client if hasattr(self.request.user, 'client') else None)
    
    @action(detail=False, methods=['post'])
    def add_to_storage(self, request):
        use_sql = request.data.get('use_sql', False)
        
        if use_sql:
            return self.add_to_storage_sql(request)
        
        warehouse_id = request.data.get('warehouse_id')
        assortment_id = request.data.get('assortment_id')
        quantity = request.data.get('quantity')
        
        if not all([warehouse_id, assortment_id, quantity]):
            return Response(
                {'error': 'Все поля обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Количество должно быть больше 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            parish = Parish.objects.create(
                warehouse_id=warehouse_id,
                assortment_id=assortment_id,
                quantity=quantity,
                created_by=request.user.client if hasattr(request.user, 'client') else None
            )
            
            return Response(
                ParishSerializer(parish).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError:
            return Response(
                {'error': 'Неверный формат количества'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def add_to_storage_sql(self, request):
        warehouse_id = request.data.get('warehouse_id')
        assortment_id = request.data.get('assortment_id')
        quantity = request.data.get('quantity')
        
        if not all([warehouse_id, assortment_id, quantity]):
            return Response(
                {'error': 'Все поля обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Количество должно быть больше 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            parish_id = SQLParishManager.create(
                warehouse_id=warehouse_id,
                assortment_id=assortment_id,
                quantity=quantity
            )
            
            return Response(
                {'id': parish_id, 'message': 'Product added to storage (SQL)'},
                status=status.HTTP_201_CREATED
            )
        except ValueError:
            return Response(
                {'error': 'Неверный формат количества'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class StorageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Storage.objects.select_related('warehouse', 'assortment').all()
    serializer_class = StorageSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_items = self.queryset.filter(quantity__lt=10)
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_warehouse(self, request):
        warehouse_id = request.query_params.get('warehouse_id')
        if warehouse_id:
            items = self.queryset.filter(warehouse_id=warehouse_id)
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data)
        return Response({'error': 'warehouse_id required'}, status=400)

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-datetime')
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def perform_create(self, serializer):
        warehouse_id = serializer.validated_data.get('warehouse_id')
        assortment_id = serializer.validated_data.get('assortment_id')
        quantity = serializer.validated_data.get('quantity')
        
        storage = Storage.objects.filter(
            warehouse_id=warehouse_id,
            assortment_id=assortment_id
        ).first()
        
        if not storage or storage.quantity < quantity:
            raise serializers.ValidationError('Недостаточно товара на складе')
        
        storage.quantity -= quantity
        storage.save()
        
        serializer.save(created_by=request.user.client if hasattr(request.user, 'client') else None)
