from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redireciona a raiz para o dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=True)),
    
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
    # APP URLS (Sem duplicatas)
    path('dashboard/', include('users.urls')), 
    path('academic/', include('academic.urls')), 
    path('classes/', include('classes.urls')),
    path('presence/', include('presence_service.urls')),
]