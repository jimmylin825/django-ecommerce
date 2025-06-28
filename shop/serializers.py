from rest_framework import serializers
from .models import Product, ProductImage, Order, OrderItem, Category, OrderMessage
from django.contrib.auth.models import User

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_cover']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_name', 'created_at', 'is_available', 'images', 'cover_image']

    def get_cover_image(self, obj):
        image = obj.get_cover_image()
        return image.image.url if image else None

class ProductBriefSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'cover_image']

    def get_cover_image(self, obj):
        image = obj.get_cover_image()
        return image.image.url if image else None

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    product = ProductBriefSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id','customer', 'customer_name', 'customer_email', 'items', 'created_at', 'status', 'total_price', 'total_quantity']

    def get_total_price(self, obj):
        return obj.total_price
    def get_total_quantity(self, obj):
        return obj.total_quantity

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id' ,'name', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OrderBriefSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','customer', 'customer_name', 'items']

class OrderMessageSerializer(serializers.ModelSerializer):
    order = OrderBriefSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    class Meta:
        model = OrderMessage
        fields = ['order', 'sender', 'content', 'is_read', 'created_at']