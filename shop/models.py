from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User



# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "商品分類"
        verbose_name_plural = "商品分類"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length = 100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    def get_cover_image(self):
        return self.images.filter(is_cover=True).first()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_cover = models.BooleanField(default=False)  # 是否為封面圖

    def __str__(self):
        return f"{self.product.name} 圖片"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待處理'),
        ('processing', '處理中'),
        ('shipped', '已出貨'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length = 100)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(default = timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"訂單編號 #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name = 'items', on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    quantity = models.PositiveIntegerField(default = 1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.id} - {self.sender.username}: {self.content[:20]}"