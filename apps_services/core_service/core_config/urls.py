"""
URL configuration for core_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include  # 'include' adicionado aqui para corrigir o NameError

urlpatterns = [
    # Painel Administrativo padrão do Django [cite: 108]
    path('admin/', admin.site.urls),
    
    # Sistema de Autenticação Completo (Login, Logout, Senha) 
    path('accounts/', include('allauth.urls')), 
    
    # Rotas do Serviço de Aulas (Geração de QR Code e CRUD de Aulas) [cite: 146, 154, 157]
    path('classes/', include('classes.urls')),
    
]