"""
Django settings for Projeto project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "loja", "templates")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tjts^qxve#o%%t3)w6pa%g82om42ay(&9@7ic6ce+yo6@p27lc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["0.0.0.0", "127.0.0.1", "localhost", "34.0.207.66", "drogariadobairro.pt"]


CSRF_TRUSTED_ORIGINS = ['https://drogariadobairro.pt', 'http://drogariadobairro.pt', "http://127.0.0.1:8000"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'loja.apps.LojaConfig',
    ### coisas adicionais
    'django_countries',
    'phonenumber_field',
    'rest_framework', ### para a api
    "corsheaders", #também para a api
    # 'mptt',
    'django_extensions',
    'django_filters',
    'rest_framework.authtoken', #Used to enable token authentication
]


AUTH_USER_MODEL = 'loja.Utilizador'
PHONENUMBER_DEFAULT_REGION = 'PT'





MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    
    
    
    "corsheaders.middleware.CorsMiddleware",

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Projeto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            TEMPLATE_DIR
            ],
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

WSGI_APPLICATION = 'Projeto.wsgi.application'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

#Database
#https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': '34.0.198.90',
        'PORT': '5432',
        'NAME': 'drogaria_db',
        'USER': 'user1',
        'PASSWORD': '12345',
        'OPTIONS':{
            "options":"-c search_path=public"
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'pt-pt'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Lisbon'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/website/assets/img/' #imagens e fotos perfil

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]




MEDIA_ROOT = BASE_DIR / 'static/website/assets/img/' #imagens e fotos perfil








# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



CORS_ALLOW_ALL_ORIGINS = True # cuidado!!!! verificar quando estiver no sercvidor. ESTA LINHA DEFINE QUEM PODE FAZER PEDIDOS À API






# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/













REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PARSER_CLASSES': ( #lidar com os dados que o cliente envia. AQUILO QUE ENTRA NA API (O JSON QUE O CLIETE ENVIOU NO PEDIDO, por exemplo)
        'rest_framework.parsers.JSONParser', #não apagar!!!!!! não apagr mesmo!
        'rest_framework_json_api.parsers.JSONParser', # não apagar!!!!!! só apagar em última instância e em caso de desespero!
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_RENDERER_CLASSES': [ #lidar com os dados que se envia para o cliente. serve para o cliente poder entender e manipular os dados.
        'rest_framework.renderers.JSONRenderer', #não apagar!!!!!! não apagar mesmo!
        'rest_framework.renderers.BrowsableAPIRenderer', #não apagar!!!!!!
        'rest_framework_json_api.renderers.JSONRenderer', # não apagar!!!!!! só apagar em última instância e em caso de desespero!
        "rest_framework.renderers.TemplateHTMLRenderer"
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
         'rest_framework.authentication.SessionAuthentication',
         "rest_framework.authentication.BasicAuthentication",
    ],

    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_json_api.filters.QueryParameterValidationFilter',
        'rest_framework_json_api.filters.OrderingFilter',
        'rest_framework_json_api.django_filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'SEARCH_PARAM': 'filter[search]',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'vnd.api+json',
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
