import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-5q%00vuh5l)05=yu9EUR14#ub(0-gktqlldgcy=ml&_!+6brijj0'

DEBUG = True

ALLOWED_HOSTS = ['*']
#CSRF_TRUSTED_ORIGINS = ['https://casqidtravels.com']
#CORS_ALLOWED_ORIGINS = ['https://casqidtravels.com']
CORS_ALLOW_ALL_ORIGINS = True

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'rest_framework',  # Django Rest Framework
    'crispy_forms',  # Django Crispy Forms
    'crispy_bootstrap5',
    'widget_tweaks',
    'storages',  # Django Storages
    'channels',  # Django Channels
    'django_celery_beat',  # Django Celery
    'django_celery_results',  # Django Celery Results
    'django_extensions',
    #'django_payments',  # Django Payments
    #'debug_toolbar',  # Django Debug Toolbar
    'core',  # Core app for site-wide functionality
    'users',
    'jobs',
    'security',
    'applications', 
    #'reviews',
    'payments',
    'notifications',
    'contact',
    'feedback',
    'services',
    'appointments',    
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-teal",
    "accent": "accent-primary",
    "navbar": "navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-teal",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
} 
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "CasQid Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "CasQid Admin Panel",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "CasQid",

    # Logo to use for your site, must be present in static files, used for brand on top left
    

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,
    "custom_css": "css/custom.css",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": 'images/logo.jpg',

    # Welcome text on the login screen
    "welcome_sign": "CasQid Travels",

    # Copyright on the footer
    "copyright": "CasQidTravels",

   
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": 'images/logo.jpg',



    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)

    "hide_apps": ["auth", "sites", "django_celery_beat", "django_celery_results"],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [
        "auth.Group",
        "auth.User",
        "sites.Site",
        "users.PasswordResetCode",
        "jobs.JobApplication",
        "django_celery_beat.PeriodicTask",
        "django_celery_results.TaskResult",
    ],
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["users", "jobs", "applications","payments", "blogs"],

    # Custom links to append to app groups, keyed on app name
    

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'travel_consultant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'appointments.context_processors.pending_appointments',
            ],
        },
    },
]

WSGI_APPLICATION = 'travel_consultant.wsgi.application'
ASGI_APPLICATION = 'travel_consultant.asgi.application'  # For Django Channels


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
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        },
    },
    
]

# Email configuration for SMTP backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'casqidtravelagency@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'sijf pekq ravo efhn'  # Replace with your email password

ADMIN_EMAIL = 'casqidtravelagency@gmail.com'  
DEFAULT_FROM_EMAIL = 'casqidtravelagency@gmail.com'   

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images) - update this section
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# When using Django Storages, override default storage only in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    # In development, use the standard file storage
    DEFAULT_FILE_STORAGE = 'django.core.mail.file_storage.FileSystemStorage'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model 
AUTH_USER_MODEL = 'users.CustomUser' 
# Mpesa API credentials 
MPESA_CONSUMER_KEY = 'your-consumer-key' 
MPESA_CONSUMER_SECRET = 'your-consumer-secret' 
MPESA_BUSINESS_SHORTCODE = 'your-shortcode' 
MPESA_PASSWORD = 'your-password' 
MPESA_TIMESTAMP = 'your-timestamp' 
MPESA_CALLBACK_URL = 'your-callback-url'

CSRF_COOKIE_SECURE = True 
SESSION_COOKIE_SECURE = True 
SECURE_BROWSER_XSS_FILTER = True 
SECURE_CONTENT_TYPE_NOSNIFF = True 
X_FRAME_OPTIONS = 'DENY' 
SECURE_HSTS_SECONDS = 3600 
SECURE_HSTS_INCLUDE_SUBDOMAINS = True 
SECURE_HSTS_PRELOAD = True 
SECURE_SSL_REDIRECT = True 
CSRF_COOKIE_HTTPONLY = True 
# Additional security settings 
SECURE_REFERRER_POLICY = 'same-origin' 
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Django Allauth settings
"""
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
"""
SITE_ID = 1

# Django Crispy Forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Django Storages settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Django Channels settings
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Django Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Django SEO settings
SEO_MODEL_TRANSLATION = 'django_seo.models.SEOModel'

# Django Payments settings
PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {}),
}

# Django Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]
CSRF_FAILURE_VIEW = 'security.views.csrf_failure'


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'