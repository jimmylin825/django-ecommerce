from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import ProductViewSet, OrderViewSet, OrderMessageViewSet, CartViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'order', OrderViewSet, basename='order')
router.register(r'message', OrderMessageViewSet, basename='message')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls))
]