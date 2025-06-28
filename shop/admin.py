from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F, DecimalField
from django.urls import reverse, path
from .models import Product, Order, OrderItem, Category, ProductImage, OrderMessage
from .forms import ProductImageForm
from django.db import models
from django.forms import CheckboxInput
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderMessageForm
# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageForm
    extra = 3  # 額外顯示幾個空白欄位新增圖片
    max_num = 10
    fields = ('image', 'is_cover', 'preview')
    readonly_fields = ('preview',)
    formfield_overrides = {
        models.BooleanField: {'widget': CheckboxInput(attrs={'class': 'form-check-input'})}
    }

    class Media:
        js = ('admin/js/only_one_cover.js',)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        cover_found = False
        for obj in instances:
            if obj.is_cover:
                # 取消同商品其他圖片的封面
                ProductImage.objects.filter(product=obj.product).update(is_cover=False)
                cover_found = True
            obj.save()
        formset.save_m2m()

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100"/>', obj.image.url)
        return "-"

    preview.short_description = "預覽圖"


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", 'category', "price", "stock", "created_at", "image_tag", 'is_available')
    list_filter = ('category', 'is_available')     #可以在後台以category過濾
    search_fields = ('name', 'category')
    list_editable = ('price', 'stock', 'is_available')

    inlines = [ProductImageInline]
    def image_tag(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if cover and cover.image:
            return format_html('<img src="{}" width="50"/>', cover.image.url)
        return "-"
    image_tag.short_description = "圖片"

    def preview_image(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if cover and cover.image:
            return format_html('<img src="{}" style="width: 80px; height: auto;" />', cover.image.url)
        return "No Image"

    preview_image.short_description = "圖片預覽"



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # 不預留空白欄位

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'status', 'created_at', 'total_price_display', 'total_quantity_display', 'message_link')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)
    fields = ('customer_name', 'status', 'created_at')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/messages/', self.admin_site.admin_view(self.order_message_view),
                 name='order_message_thread'),
        ]
        return custom_urls + urls

    def order_message_view(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        messages = order.messages.order_by('created_at')

        if request.method == 'POST':
            form = OrderMessageForm(request.POST)
            if form.is_valid():
                msg = form.save(commit=False)
                msg.order = order
                msg.sender = request.user
                msg.is_read = True
                msg.save()
                return redirect('admin:order_message_thread', order_id=order.id)
        else:
            form = OrderMessageForm()

        return render(request, 'admin/order_message_thread.html', {
            'order': order,
            'messages': messages,
            'form': form,
            'opts': self.model._meta,
        })

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 使用 annotate 計算每筆訂單的總金額
        return qs.annotate(
            total_price_value=Sum(
                F('items__quantity') * F('items__price'),
                output_field=DecimalField()))

    def total_price_display(self, obj):
        value = getattr(obj, 'total_price_value', 0)
        if value is None:
            return "$0.00"
        return f"${value:.2f}"

    def message_link(self, obj):
        url = reverse('admin:order_message_thread', args=[obj.id])
        return format_html('<a class="button" href="{}">查看留言</a>', url)

    message_link.short_description = '留言紀錄'

    total_price_display.admin_order_field = 'total_price_value'
    total_price_display.short_description = '總金額'

    def total_quantity_display(self, obj):
        return obj.total_quantity

    def save_formset(self, request, form, formset, change):
        if formset.model == OrderMessage:
            instances = formset.save(commit=False)
            for instance in instances:
                # 僅在新留言時設定 sender，避免竄改原留言
                if not instance.pk:
                    instance.sender = request.user
                instance.save()
            formset.save_m2m()
        else:
            formset.save()

    total_quantity_display.short_description = '總數量'

admin.site.site_header = "電商後台"
admin.site.index_title = "控制台"

def stats_link(obj=None):
    url = reverse('sales_stats')
    return format_html('<a class="button" href="{}">📊 銷售統計</a>', url)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)




admin.site.register(OrderMessage)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
