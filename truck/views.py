# views.py
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('expense_list')  # hoặc trang chính
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})
