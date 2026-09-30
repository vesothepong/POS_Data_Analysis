import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-this")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework",
    "accounts", "products", "sales", "forecasting", "analytics", "dashboard", "shop",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates", "DIRS":[BASE_DIR/"templates"], "APP_DIRS":True, "OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages","django.template.context_processors.media","shop.context_processors.cart_badge"]}}]
WSGI_APPLICATION = "config.wsgi.application"

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
if DB_ENGINE == "mysql":
    DATABASES = {"default": {"ENGINE":"django.db.backends.mysql", "NAME":os.getenv("DB_NAME","inventory_forecasting"), "USER":os.getenv("DB_USER","root"), "PASSWORD":os.getenv("DB_PASSWORD",""), "HOST":os.getenv("DB_HOST","127.0.0.1"), "PORT":os.getenv("DB_PORT","3306"), "OPTIONS":{"charset":"utf8mb4"}}}
else:
    DATABASES = {"default": {"ENGINE":"django.db.backends.sqlite3", "NAME":BASE_DIR/"db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Phnom_Penh"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR/"static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR/"media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: "danger"}  # Bootstrap has alert-danger, not alert-error
# The API is admin-only (is_staff), matching the web pages.
REST_FRAMEWORK = {"DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAdminUser"]}
