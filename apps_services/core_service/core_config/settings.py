import os
from pathlib import Path

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de Segurança
SECRET_KEY = 'sua-chave-secreta-aqui' 
DEBUG = True
ALLOWED_HOSTS = []

# Aplicações Instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', 

    # Apps de Terceiros
    'rest_framework',         
    'corsheaders',            
    'allauth',                
    'allauth.account',        
    'allauth.socialaccount',
    'simple_history',         

    # Meus Apps de Microserviço 
    'users',     
    'academic',  
    'classes',   
]

# Configurações de Autenticação (Allauth atualizado para versão 2026)
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'users.User' 

# Correção dos Warnings do Allauth
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none' 
LOGIN_REDIRECT_URL = '/dashboard/' 

# Middlewares 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'core_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core_config.wsgi.application'

# Banco de Dados SQLite (Ativo para Desenvolvimento)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuração do PostgreSQL (Comentada para Etapa futura)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'frequencia_db',
#         'USER': 'daniel_admin',
#         'PASSWORD': 'sua_senha_aqui',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache com Redis (Sistemas Distribuídos)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Mensageria com Celery e RabbitMQ
CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Segurança Física: Ranges de IP da UFVJM
UNIVERSIDADE_IP_RANGES = [
    '127.0.0.1',        # Localhost
    '192.168.0.0/16',   # Rede interna
    '200.131.0.0/16',   # Range UFVJM
]