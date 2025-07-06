from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="電子信箱",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入電子信箱'
        })
    )

    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入密碼'
        })
    )

    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請再次輸入密碼'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': '帳號',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入帳號'
            }),
        }