"""
Django settings for backend project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.templatetags.static import static

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================== SECURITY & ENVIRONMENT ====================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.ngrok-free.app',
]


# ==================== APPLICATION DEFINITION ====================
INSTALLED_APPS = [
    # --- Unfold Apps (Must be before django.contrib.admin) ---
    'unfold',
    'unfold.contrib.filters',  # Adds beautiful sidebar filters
    'unfold.contrib.forms',    # Adds Tailwind forms
    'unfold.contrib.import_export', # Integration with django-import-export
    'unfold.contrib.guardian', # Object level permissions (optional)

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party apps
    'social_django',
    
    # Custom Apps
    'core',
    'accounts',
    'products',
    'cart',
    'checkout',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Social Django middleware
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'backend.urls'


# ==================== TEMPLATES CONFIGURATION ====================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Social Django context processors
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'core.context_processors.promotional_popup',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# ==================== DATABASE CONFIGURATION ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==================== PASSWORD VALIDATION ====================
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


# ==================== INTERNATIONALIZATION ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC' # Change to 'Africa/Nairobi' if needed
USE_I18N = True
USE_TZ = True


# ==================== STATIC & MEDIA FILES ====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================== CUSTOM USER MODEL ====================
AUTH_USER_MODEL = 'accounts.User'


# ==================== AUTHENTICATION BACKENDS ====================
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


# ==================== GOOGLE OAUTH2 CONFIGURATION ====================
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False


# ==================== SOCIAL AUTH PIPELINE ====================
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'accounts.pipeline.create_user_from_google', # Your custom pipeline
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


# ==================== LOGIN/REDIRECT URLS ====================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'


# ==================== EMAIL CONFIGURATION ====================
# backend/settings.py

# ==================== EMAIL CONFIGURATION ====================
# Use SMTP to send real emails
# ==================== EMAIL CONFIGURATION ====================
# Use SMTP to send real emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Pull strictly from .env
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')

# Convert string '587' from .env to integer 587
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))

# Convert string 'True' from .env to boolean True
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'

# Credentials
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Matches DEFAULT_FROM_EMAIL in your .env
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')


# ==================== SECURITY SETTINGS ====================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# ==================== UNFOLD THEME SETTINGS (OPTIMIZED) ====================
UNFOLD = {
    "SITE_TITLE": "Ari Farm Admin",
    "SITE_HEADER": "Ari Farm Management",
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("images/logo.png"),  # Uncomment if you have a logo
    "SITE_SYMBOL": "agriculture",  # Material Symbol icon name

    # 🟢 BRANDING COLORS: Optimized for Unfold/Tailwind
    "COLORS": {
        "primary": {
            "50": "240 253 244",
            "100": "220 252 231",
            "200": "187 247 208",
            "300": "134 239 172",
            "400": "74 222 128",
            "500": "34 197 94",  # Base Green
            "600": "22 163 74",
            "700": "21 128 61",
            "800": "22 101 52",
            "900": "20 83 45",
            "950": "5 46 22",
        },
    },

    # 🟢 SIDEBAR NAVIGATION: Grouped for UX
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False, # Hide default list to use our custom groups
        "navigation": [
            {
                "title": "Sales & Logistics",
                "separator": True,
                "items": [
                    {
                        "title": "Orders",
                        "icon": "shopping_cart_checkout",
                        "link": reverse_lazy("admin:checkout_order_changelist"),
                        "badge": "sample_pending_count", # You can create a template tag for this later
                    },
                    {
                        "title": "Delivery Zones",
                        "icon": "local_shipping",
                        "link": reverse_lazy("admin:checkout_deliveryzone_changelist"),
                    },
                    {
                        "title": "Active Carts",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:cart_cart_changelist"),
                    },
                ],
            },
            {
                "title": "Product Catalog",
                "separator": True,
                "items": [
                    {
                        "title": "All Products",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:products_product_changelist"),
                    },
                    {
                        "title": "Baskets & Combos",
                        "icon": "shopping_basket",
                        "link": reverse_lazy("admin:products_productbasket_changelist"),
                    },
                    {
                        "title": "Merchandise",
                        "icon": "checkroom",
                        "link": reverse_lazy("admin:products_merchandise_changelist"),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy("admin:products_category_changelist"),
                    },
                ],
            },
            {
                "title": "Marketing & Content",
                "separator": True,
                "items": [
                    {
                        "title": "Recipes",
                        "icon": "restaurant_menu",
                        "link": reverse_lazy("admin:products_recipe_changelist"),
                    },
                    {
                        "title": "Promotions / Popups",
                        "icon": "campaign",
                        "link": reverse_lazy("admin:core_promotionalpopup_changelist"),
                    },
                    {
                        "title": "Gallery & Media",
                        "icon": "collections",
                        "link": reverse_lazy("admin:core_galleryitem_changelist"),
                    },
                    {
                        "title": "Product Reviews",
                        "icon": "reviews",
                        "link": reverse_lazy("admin:products_productreview_changelist"),
                    },
                ],
            },
            {
                "title": "User Management",
                "separator": True,
                "items": [
                    {
                        "title": "Customers & Staff",
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": "Groups & Permissions",
                        "icon": "lock_person",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
    
    # 🟢 EXTRA TWEAKS
    "TABS": [
        {
            "models": ["checkout.order"],
            "items": [
                {"title": "All Orders", "link": reverse_lazy("admin:checkout_order_changelist")},
                # Note: You can add filtered links here if you create custom views or use query params
            ],
        },
    ],
}