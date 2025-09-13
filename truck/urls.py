
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
       # Trang đăng nhập mặc định của Django
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('', include('expenses.urls')),  # Trang chủ dùng views của app expenses





]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

