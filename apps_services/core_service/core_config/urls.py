from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from users.views import dashboard

urlpatterns = [
    # Redireciona a página inicial (http://127.0.0.1:8000/) para o login
    path('', RedirectView.as_view(url='/accounts/login/'), name='index'),
    
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('classes/', include('classes.urls')),
    
    # Rota do Dashboard personalizado
    path('dashboard/', dashboard, name='dashboard'),
]