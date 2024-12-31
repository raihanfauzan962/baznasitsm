from pathlib import Path
import os
import environ
from google.oauth2 import service_account

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Secret key for cryptographic signing (keep this secure and do not share it)
SECRET_KEY = env("SECRET_KEY")

# Debug mode for development (False in production)
DEBUG = env("DEBUG")

# Allowed hosts for the application (domains/IPs permitted to access the app)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Installed apps (includes Django's default apps and custom apps)
INSTALLED_APPS = [
    'jazzmin',  # Customized admin interface
    'django.contrib.admin',  # Admin site functionality
    'django.contrib.auth',  # Authentication framework
    'django.contrib.contenttypes',  # Content types framework
    'django.contrib.sessions',  # Session framework
    'django.contrib.messages',  # Messaging framework
    'django.contrib.staticfiles',  # Static file management
    "django.contrib.sites",  # Multi-site support
    "crispy_forms",  # Form rendering support
    "crispy_bootstrap5",  # Bootstrap 5 support for forms
    "allauth",  # Django Allauth for authentication
    "allauth.account",  # Allauth account management
    "allauth.socialaccount",  # Allauth social account integration
    "allauth.socialaccount.providers.google",  # Google provider for Allauth
    "storages",  # Django storages for handling storage backends
    "accounts.apps.AccountsConfig",  # Custom user account app
    "pages.apps.PagesConfig",  # Pages app for static pages
    "incident_report.apps.IncidentReportConfig",  # Incident report app
    "service_request.apps.ServiceRequestConfig",  # Service request app
    "dashboard.apps.DashboardConfig",  # Dashboard app
]

# Middleware (handles requests/responses processing)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# URL configuration module
ROOT_URLCONF = 'django_project.urls'

# Template configuration (defines directories and context processors)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Custom templates directory
        'APP_DIRS': True,  # Enables app-specific templates
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

# WSGI application (entry point for WSGI-compatible web servers)
WSGI_APPLICATION = 'django_project.wsgi.application'

# Database configuration (PostgreSQL in this case)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database backend
        'NAME': env("DATABASE_NAME"),  # Database name
        'USER': env("DATABASE_USER"),  # Database username
        'PASSWORD': env("DATABASE_PASSWORD"),  # Database password
        'HOST': env("DATABASE_HOST"),  # Database host (e.g., localhost)
        'PORT': env("DATABASE_PORT"),  # Database port
    }
}

# Password validation rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'  # Default language
TIME_ZONE = 'Asia/Jakarta'  # Default timezone
USE_I18N = True  # Enable internationalization
USE_TZ = True  # Enable timezone support

# Static and media files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Additional static files directory
STATIC_ROOT = BASE_DIR / "staticfiles"  # Directory for collected static files
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = f"https://storage.googleapis.com/{env('GS_BUCKET_NAME')}/"  # Media files URL
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"  # GCS for media files

# Google Cloud Storage credentials
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, env("GS_CREDENTIALS_FILE"))
)
GS_PROJECT_ID = env("GS_PROJECT_ID")
GS_BUCKET_NAME = env("GS_BUCKET_NAME")

# Authentication configuration
AUTH_USER_MODEL = "accounts.CustomUser"  # Custom user model
LOGIN_REDIRECT_URL = "home"  # Redirect URL after login
ACCOUNT_LOGOUT_REDIRECT = "home"  # Redirect URL after logout
SITE_ID = 2  # Current site ID
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # Default authentication backend
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth backend
)

# Email settings (using Gmail SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("EMAIL_HOST_USER")

# django-crispy-forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# django-allauth settings
ACCOUNT_SESSION_REMEMBER = True  # Remember session
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False  # Password entered once during signup
ACCOUNT_USERNAME_REQUIRED = False  # No username required
ACCOUNT_AUTHENTICATION_METHOD = "email"  # Email-based authentication
ACCOUNT_EMAIL_REQUIRED = True  # Email is mandatory
ACCOUNT_UNIQUE_EMAIL = True  # Email must be unique
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],  # OAuth scopes
        'AUTH_PARAMS': {'access_type': 'online'},  # Access type
        'OAUTH_PKCE_ENABLED': True,  # Enable PKCE
    }
}
SOCIALACCOUNT_ADAPTER = "accounts.adapters.CustomSocialAccountAdapter"  # Custom adapter

# Jazzmin configuration (custom admin interface)
JAZZMIN_SETTINGS = {
    "site_title": "BAZNAS ITSM Admin",  # Title of the admin site
    "site_header": "BAZNAS ITSM",  # Header title
    "site_brand": "BAZNAS ITSM",  # Branding
    "site_logo": r"C:\Users\raiha\OneDrive\Desktop\ITSM BAZNAS\static\images\logo_baznas.png",  # Logo path
    "welcome_sign": "Welcome to the BAZNAS ITSM Admin Dashboard",  # Welcome message
    "copyright": "BAZNAS",  # Copyright notice
    "hide_admin_version": True,  # Hide Django admin version
    "show_sidebar": True,  # Display sidebar
    "navigation_expanded": True,  # Expand navigation by default
    "custom_css": r"C:\Users\raiha\OneDrive\Desktop\ITSM BAZNAS\static\css\customadmin.css",  # Custom CSS file
    "show_ui_builder": False,  # Hide UI builder

    "topmenu_links": [
        {"name": "Incident Reports", "url": "admin:incident_report_incidentreport_changelist"},
        {"name": "Service Requests", "url": "admin:service_request_servicerequest_changelist"},
    ],

    "usermenu_links": [
        {"model": "auth.user"},
    ],

    "icons": {
        "auth": "fas fa-user",               
        "auth.User": "fas fa-user",              
        "auth.Group": "fas fa-users",                
        "accounts.CustomUser": "fas fa-user",            
        "account.EmailAddress": "fas fa-envelope", 
        "sites": "fas fa-globe",                     
        "sites.Site": "fas fa-globe", 
        
        "incident_report.IncidentReport": "fas fa-solid fa-ticket",
        "incident_report.Category": "fas fa-layer-group",
        "incident_report.SubCategory": "fas fa-solid fa-list",
        "incident_report.Issue": "fas fa-exclamation-triangle",
        "incident_report.AffectedDevice": "fas fa-desktop",
        "incident_report.Building": "fas fa-building",
        "incident_report.Floor": "fas fa-th-large",
        
        "service_request.ServiceRequest": "fas fa-solid fa-ticket",
        "service_request.Category": "fas fa-layer-group",
        "service_request.ServiceItem": "fas fa-box",
        "service_request.ServiceItemForm": "fas fa-clipboard-list",
        
        "Dashboard.TicketSummary": "fa-solid fa-newspaper",
        
        
    },
    
    "order_with_respect_to": [
        "Dashboard",
        "Dashboard.TicketSummary",
        
        "Incident_Report",  
        "Incident_Report.IncidentReport",
        "Incident_Report.Category",
        "Incident_Report.SubCategory",
        "Incident_Report.Issue",
        "Incident_Report.AffectedDevice",
        "Incident_Report.Building",
        "Incident_Report.Floor",
        
        "Service_Request",
        "Service_Request.ServiceRequest",
        "Service_Request.Category",
        "Service_Request.ServiceItem",
        "Service_Request.ServiceItemForm",
        
    ],

}

JAZZMIN_UI_TWEAKS = {
    "theme": "cerulean",  # Set theme color
}
