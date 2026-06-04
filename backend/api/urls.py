from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'assortment', AssortmentViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'kits', KitViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'styles', StyleViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'parishes', ParishViewSet)
router.register(r'storage', StorageViewSet)
router.register(r'expenses', ExpenseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', AuthView.as_view(), name='auth'),
]
