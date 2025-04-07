from datetime import timedelta
from pathlib import Path
from decouple import config
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c6d!*9p2jsdyu^6&dbr8&a_67dy)ir2po6b%kwk^b2pkq4r&4t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# to test stripe payment with ngrok "6255-156-201-137-99.ngrok-free.app"
# to test paypal payment with ngrok "3fae-156-201-71-243.ngrok-free.app"
ALLOWED_HOSTS = ['6255-156-201-137-99.ngrok-free.app',
                 '127.0.0.1',
                 '3fae-156-201-71-243.ngrok-free.app',
                 'localhost']


# Application definition

INSTALLED_APPS = [
    # Apps
    'accounts',
    'products',
    'orders',
    'payment',
    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Thrird-party
    'rest_framework',
    'dj_rest_auth',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# -- REST FRAMEWORK --- 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

## AUTH SETTINGS

REST_USE_JWT = True
CSRF_COOKIE_SECURE = True

AUTH_USER_MODEL = 'accounts.CustomUser'

SIMPLE_JWT = {
  "ACCESS_TOKEN_LIFETIME" : timedelta(days= 15),
  "REFRECH_TOKEN_LIFETIME" : timedelta(days= 1),
  "BLACKLIST_AFTER_ROTATION": True, 
  "AUTH_HEADER_TYPES": ("Bearer",),  
  "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),

}

## STATIC AND MEDIA SETTINGS

STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

BACKEND_DOMAIN = config('BACKEND_DOMAIN')
# Payment settings
# -- STRIPE -- 
STRIPE_PUBLISHABLE_KEY  = config('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
PAYMENT_SUCCESS_URL = config("PAYMENT_SUCCESS_URL")
PAYMENT_CANCEL_URL = config("PAYMENT_CANCEL_URL")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")


# -- PAYPAL --
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = config('PAYPAL_SECRET')
PAYPAL_MODE = config('PAYPAL_MODE')  # Change to 'sandbox'  # Change to 'live' for production

INSTALLED_APPS += [
    'paypal.standard.ipn',
]

# PayPal IPN (Instant Payment Notification) URL
PAYPAL_NOTIFY_URL = config('PAYPAL_NOTIFY_URL')
PAYPAL_RETURN_URL = config('PAYPAL_RETURN_URL')
PAYPAL_CANCEL_URL = config('PAYPAL_CANCEL_URL')
