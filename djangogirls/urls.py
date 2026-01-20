from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog
from core.views import coc_legacy

from django.contrib.auth import views as auth_views

from django.urls import reverse_lazy

from blog.views import comment_image_upload

urlpatterns = [
    # CKEditor public upload override (must be BEFORE the include)
    path("ckeditor5/image_upload/", comment_image_upload, name="comment_image_upload"),

    # Default CKEditor 5 URLs (for admin etc.)
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    re_path(r"^coc/(?:(?P<lang>[a-z-]+)/)?$", coc_legacy, name="coc_legacy"),
    # Redirection for old CoC's flatpages:
    path("pages/coc/", RedirectView.as_view(url="/coc/", permanent=True)),
    path("pages/coc-es-la/", RedirectView.as_view(url="/coc/es/", permanent=True)),
    path("pages/coc-fr/", RedirectView.as_view(url="/coc/fr/", permanent=True)),
    path("pages/coc-kr/", RedirectView.as_view(url="/coc/ko/", permanent=True)),
    path("pages/coc-pt-br/", RedirectView.as_view(url="/coc/pt-br/", permanent=True)),
    path("pages/coc/rec/", RedirectView.as_view(url="/coc/pt-br/", permanent=True)),
    #path("blog/", include("blog.urls", namespace="blog")),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="event/password_reset_form.html",
            email_template_name="event/password_reset_email.txt",
            subject_template_name="event/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),

    # --- After form submitted ("we sent you an email") ---
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="event/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    # --- Link from email: set new password ---
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="event/change_password.html",   # reuse your template
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),

    # --- After successful change ---
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="event/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]


urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    # Redirect old links:
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path("pages/in-your-city/", RedirectView.as_view(url="/organize/", permanent=True)),
    path("admin", RedirectView.as_view(url="/admin/", permanent=True)),
    path("admin/core/eventpage/<int>/", RedirectView.as_view(pattern_name="admin:core_event_change")),
    # Admin link for password reset
    # See:
    # https://github.com/darklow/django-suit/blob/92a745d72935622220eca80edfce779419c30094/suit/templates/admin/
    # login.html#L61

    path(
        "admin/password_reset/",
        RedirectView.as_view(url="/account/password_reset", permanent=True),
        name="admin_password_reset",
    ),
    path("tinymce/", include("tinymce.urls")),
    # Regular links:
    path("admin/", admin.site.urls),
    path("pages/", include("django.contrib.flatpages.urls")),
    path("account/", include("django.contrib.auth.urls")),
    path("coach/", include("coach.urls")),
    path("contact/", include("contact.urls")),
    ###
    #path("contact/", include(("contact.urls", "contact"), namespace="contact")),
    #path("contact/", RedirectView.as_view(pattern_name="contact:contact"), name="contact_form"),
    ###
    path("donate/", include("donations.urls")),
    path("organize/", include("organize.urls")),
    path("story/", include("story.urls")),
    path("jobs/", include("jobboard.urls")),
    # path('', include('sponsor.urls')),
    path("", include("applications.urls")),
    #path("", include("core.urls")),
    path("", include(("core.urls", "core"), namespace="core")),
    path("blog/", include(("blog.urls", "blog"), namespace="blog")),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
