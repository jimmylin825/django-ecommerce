from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.shortcuts import redirect
from django.contrib import messages
# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
        else:
            print(form.errors)  # 調試用
            messages.error(request, '註冊失敗，請檢查輸入內容')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, 'users/login.html', {"error": "帳號或密碼錯誤"})
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('product_list')
