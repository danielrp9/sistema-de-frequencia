from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from users.views import AccountLoginView

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=True)),

    path('admin/', admin.site.urls),
    path('accounts/login/', AccountLoginView.as_view(), name='account_login'),
    path(
        'accounts/signup/',
        RedirectView.as_view(
            url='/dashboard/cadastro/escolha/',
            permanent=True
        ),
        name='account_signup'
    ),
    path('accounts/', include('allauth.urls')),

    # APP URLS (Sem duplicatas)
    path('dashboard/', include('users.urls')),
    path('academic/', include('academic.urls')),
    path('classes/', include('classes.urls')),
    path('presence/', include('presence_service.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
