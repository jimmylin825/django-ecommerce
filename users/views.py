from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.shortcuts import redirect
# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 註冊後自動登入
            return redirect('product_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form, 'error' : '發生錯誤請重新嘗試'})


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
