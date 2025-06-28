from django.urls import path
from . import views


urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name = 'cart_view'),
    path('update-cart/<int:product_id>/', views.update_cart, name = 'update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_cart, name = 'remove_from_cart'),
    path('create-order/', views.create_order, name='create_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('sales-stats/', views.sales_stats, name='sales_stats'),
    path('orders/<int:order_id>/report/', views.customer_report, name='customer_report'),
]