from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from users.views import dashboard

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/'), name='index'),
    
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('classes/', include('classes.urls')),
    
    path('dashboard/', dashboard, name='dashboard'),
]