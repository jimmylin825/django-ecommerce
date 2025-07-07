from rest_framework import viewsets, permissions, filters as drf_filters, status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from .models import Product, Order, OrderMessage, OrderItem
from .serializers import ProductSerializer, OrderSerializer, OrderMessageSerializer, ProductBriefSerializer
from django_filters import rest_framework as filters
from .filters import ProductFilter
from rest_framework.decorators import action
from django.utils import timezone

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

class OrderViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [filters.DjangoFilterBackend, drf_filters.OrderingFilter]
    ordering_fields = ['created_at', 'status']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Order.objects.filter(customer = user).order_by('-created_at')
        else:
            guest_token = self.request.session.get('guest_token')
            return Order.objects.filter(customer=None, guest_token = guest_token).order_by('-created_at')


class CartViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return Response({'error': '購物車為空，無法建立訂單'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_authenticated:
            customer = request.user
            customer_name = request.user.username
            customer_email = request.user.email
        else:
            customer = None
            customer_name = '匿名用戶'
            customer_email = ''

        order = Order.objects.create(
            customer=customer,
            customer_name=customer_name,
            customer_email=customer_email,
            created_at=timezone.now()
        )

        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue

            if product.stock < quantity:
                return Response({
                    'error': f"{product.name} 庫存不足，僅剩 {product.stock} 件。"
                }, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            product.stock -= quantity
            product.save()

        request.session['cart'] = {}  # 清空購物車

        return Response({'message': '訂單已成功建立', 'order_id': order.id}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def order_list(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                product_data = ProductBriefSerializer(product).data
                cart_items.append({
                    'product': product_data,
                    'quantity': quantity,
                    'subtotal': round(product.price * quantity, 2)
                })
            except Product.DoesNotExist:
                continue
        return Response(cart_items)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = str(request.data.get('product_id'))
        quantity = int(request.data.get('quantity', 1))

        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + quantity
        request.session['cart'] = cart
        return Response({'message': '已加入購物車', 'cart': cart})

    @action(detail=False, methods=['post'])
    def remove(self, request):
        product_id = str(request.data.get('product_id'))

        cart = request.session.get('cart', {})
        cart.pop(product_id, None)
        request.session['cart'] = cart
        return Response({'message': '已移除商品', 'cart': cart})

class OrderMessageViewSet(viewsets.ModelViewSet):
    serializer_class = OrderMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    orders = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return OrderMessage.objects.filter(order__customer = user)
        else:
            guest_token = self.request.session.get('guest_token')
            return OrderMessage.objects.filter(order__customer=None, guest_token=guest_token)

    def create(self, request, *args, **kwargs):
        serializer = OrderMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': '無法刪除已發送的訊息'}, status=403)
    def update(self, request, *args, **kwargs):
        # 禁用修改
        return Response({'detail': '無法修改已發送的訊息'}, status=403)
    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': '無法修改訊息'}, status=403)

