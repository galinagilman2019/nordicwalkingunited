import os
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .utils.sanitize import sanitize


def gettext(s):
    """
    i18n passthrough
    """
    return s


from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

BASE_URL = "https://djangogirls.org"

DEBUG = os.getenv("DJANGO_DEBUG") != "FALSE"

SECRET_KEY = "hello!" if DEBUG else os.getenv("DJANGO_SECRET_KEY")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
#ALLOWED_HOSTS = ["NWU.pythonanywhere.com"]
#ALLOWED_HOSTS = [
#    "nwu.pythonanywhere.com",
#    "www.nordicwalkingunited.org",
#    "nordicwalkingunited.org",
#]
ALLOWED_HOSTS = ["nwu.pythonanywhere.com", "www.nordicwalkingunited.org", "nordicwalkingunited.org"]
CSRF_TRUSTED_ORIGINS = ["https://nwu.pythonanywhere.com", "https://www.nordicwalkingunited.org", "https://nordicwalkingunited.org"]

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "widget_tweaks",
    "django_ckeditor_5",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "adminsortable2",
    "django_bleach",
    "django_date_extensions",
    "django_unused_media",
    "django_extensions",
    "storages",
    "markdown_deux",
    "easy_thumbnails",
    'django_recaptcha',
    "django_countries",
    "gulp_rev",
    "core",
    #"blog",
    "blog.apps.BlogConfig",
    "applications",
    "organize",
    "patreonmanager",
    "story",
    "sponsor",
    "coach",
    "contact",
    "pictures",
    "donations",
    "jobboard",
    "globalpartners",
    "stripe_payments",
    "django.contrib.sitemaps",
    "crispy_forms",
    "crispy_bootstrap4",
    "mathfilters"


    # third-party apps



]
SITE_ID = 1
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"
MIDDLEWARE = [
    "core.middleware.AdminToPythonAnywhereMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "djangogirls.urls"

WSGI_APPLICATION = "djangogirls.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Database
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / "db.sqlite3",  # Now BASE_DIR is a Path object
#    }
#}
DATABASES = {
    'default': dj_database_url.config(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", gettext("English")),
    ("ar", gettext("Arabic")),
    ("pt-br", gettext("Brazilian Portuguese")),
    ("nl", gettext("Dutch")),
    ("fr", gettext("French")),
    ("de", gettext("German")),
    ("he", gettext("Hebrew")),
    ("ko", gettext("Korean")),
    ("fa", gettext("Persian")),
    ("pt", gettext("Portuguese")),
    ("ru", gettext("Russian")),
    ("es", gettext("Spanish")),
]

TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.statistics",
            ],
            "debug": DEBUG,
        },
    },
]

# Custom

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

AUTH_USER_MODEL = "core.User"


THUMBNAIL_PRESERVE_EXTENSIONS = True
THUMBNAIL_ALIASES = {
    "": {
        "coach": {"size": (160, 160), "crop": "smart"},
        "sponsor": {"size": (204, 204), "crop": False},
    },
}

#STATICFILES_DIRS = [
#    BASE_DIR / "PP" / "prod",
#]
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # for collectstatic if used
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = "/uploads/"
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
#CKEDITOR_UPLOAD_PATH = "user_uploads/"  # This creates /uploads/user_uploads/
import datetime
CKEDITOR_UPLOAD_PATH = f"user_uploads/{datetime.date.today().year}/{datetime.date.today().month}/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "any"
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_RESTRICT_BY_USER = False  # Optional
DJANGO_GULP_REV_PATH = os.path.join(BASE_DIR, "static/rev-manifest.json")
LOGIN_URL = "admin:login"

if "GITHUB_ACTIONS" in os.environ:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/source")]
elif DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/local")]
else:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/build")]


STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])

MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_APIKEY")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Nordic Walking United <nordicwalkingunited@gmail.com>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'smtp.gmail.com'            # if using Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
#EMAIL_HOST_USER = os.environ.get("glnglmn@gmail.com")  # e.g. your@gmail.com
#EMAIL_HOST_PASSWORD='xkmu hell wsbh ohol'
#EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
#EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASS")
EMAIL_HOST_USER='nordicwalkingunited@gmail.com'
EMAIL_HOST_PASSWORD='uwwy lpbh phst djuz'
ENABLE_SLACK_NOTIFICATIONS = sanitize(os.environ.get("ENABLE_SLACK_NOTIFICATIONS", False), bool)
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_TEAM_ID = os.environ.get("SLACK_TEAM_ID")
SLACK_INVITE_CHANNEL_IDS = os.environ.get("SLACK_INVITE_CHANNEL_IDS", "").split(",")
SLACK_INVITE_LINK = os.environ.get("SLACK_INVITE_LINK", "")

RECAPTCHA_PUBLIC_KEY = "6LenV8EqAAAAAKT0qchwylOJSbGr-sDmyK53yyk3"
RECAPTCHA_PRIVATE_KEY = "6LenV8EqAAAAAJSFK7QGRyeQJaaYBTTASeoT8ItD"
# Using new No Captcha reCaptcha with SSL
NOCAPTCHA = True

TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")

NOSE_ARGS = []

# Optionally enable coverage reporting
if os.environ.get("COVERAGE") == "TRUE":
    NOSE_ARGS += [
        "--with-coverage",
        "--cover-package=core,applications,patreonmanager",
    ]

MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
        },
        "safe_mode": "escape",
    },
    "trusted": {
        "extras": {
            "code-friendly": None,
        },
        "safe_mode": False,
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG

APPEND_SLASH = True

GAPPS_ADMIN_SDK_SCOPES = "https://www.googleapis.com/auth/admin.directory.user"
GAPPS_PRIVATE_KEY_ID = os.environ.get("GAPPS_PRIVATE_KEY_ID", "")
GAPPS_PRIVATE_KEY = os.environ.get("GAPPS_PRIVATE_KEY", "")

STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")

FLICKR_DJANGO_GIRLS_USER_ID = os.environ.get("FLICKR_DJANGO_GIRLS_USER_ID")
FLICKR_API_KEY = os.environ.get("FLICKR_API_KEY")

# ***** DEBUG TOOLBAR *****

DEBUG_TOOLBAR = DEBUG and os.environ.get("DEBUG_TOOLBAR", "no") == "yes"

if DEBUG_TOOLBAR:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: not request.is_ajax(),
    }
def show_toolbar(request):
    return True
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}

RECAPTCHA_TESTING = os.environ.get("RECAPTCHA_TESTING") == "True"
if RECAPTCHA_TESTING:
    SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

BLEACH_ALLOWED_TAGS = ["p", "b", "i", "u"]
BLEACH_ALLOWED_ATTRIBUTES = ["title"]
BLEACH_STRIP_TAGS = True
BLEACH_STRIP_COMMENTS = True

TUMBLR_API_KEY = os.environ.get("TUMBLR_API_KEY")
TUMBLR_API_BASE_URL = os.environ.get("TUMBLR_API_BASE_URL", "https://api.tumblr.com/v2")
TUMBLR_BLOG_HOSTNAME = os.environ.get("TUMBLR_BLOG_HOSTNAME", "blog.djangogirls.org")

MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN")


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),  # File in your project folder
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]
CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
        ],
    },

    # 🔹 For Comment: ONLY image upload button

    "comment": {
        "language": {"ui": "en", "content": "en"},

        "toolbar": [
            "uploadImage",
             "|",
             "undo",
             "redo",
        ],


        "height": 200,
        "width": "100%",

        # Toolbar that appears when the image is selected
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "toggleImageCaption",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "imageStyle:side",
            ],
            "styles": [
                "alignLeft",
                "alignCenter",
                "alignRight",
                "side",
            ],
        },
    },



    # 🔹 Full editor for posts, unchanged
    "extends": {
        "language": "en",
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "codeBlock",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "insertImage",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
            "sourceEditing",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
                "toggleImageCaption",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
            ]
        },
    },
}

"""
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload"
        ],
    },
    "comment": {
        "language": {"ui": "en", "content": "en"},
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
        ],
    },
    "extends": {
        "language": "en",
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "codeBlock",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "insertImage",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
            "sourceEditing",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
                "toggleImageCaption",
                "|"
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
            ]
        },
    },
}
"""
