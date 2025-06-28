from django import forms
from .models import ProductImage, OrderMessage

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_cover']
        labels = {'is_cover': '設為封面'}

class OrderMessageForm(forms.ModelForm):
    class Meta:
        model = OrderMessage
        fields = ['content']
