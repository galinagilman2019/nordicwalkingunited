from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from story.sitemap import BlogSiteMap

from .sitemap import StaticViewSitemap
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings

sitemaps = {"website": StaticViewSitemap, "blog": BlogSiteMap}

#app_name = "core"
urlpatterns = [
    path("", views.index, name="index"),
    path("nwu-rules/", views.nwu_rules, name="nwu_rules"),
    path("group/<int:pk>/events/", views.group_events, name="group_events"),
    path("events/", views.events, name="events"),
    path("events/map/", views.events_map, name="events_map"),
    path("events/calendar.ics", views.events_ical, name="icalendar"),
    path("events/<uuid:uuuid>/rules/", views.event_rules, name="event_rules"),

    path("submission/<uuid:pk>/delete/", views.delete_submission, name="delete-submission"),

    #path("resources/", views.resources, name="resources"),

    path("tutorials/", views.nwu_resources, name="nwu_resources"),
    path("tutorials/<slug:slug>/", views.nwu_resource_detail, name="nwu_resource_detail"),

    path("newsletter/", views.newsletter, name="newsletter"),
    path("faq/", views.faq, name="faq"),
    path("faq_org/", TemplateView.as_view(template_name="core/faq_org.html"), name="faq_org"),
    path("foundation/", views.foundation, name="foundation"),
    path("foundation/governing-document/", views.governing_document, name="foundation-governing-document"),
    path("contribute/", views.contribute, name="contribute"),
    path("2015/", views.year_2015, name="year_2015"),
    path("2016-2017/", views.year_2016_2017, name="year_2016_2017"),
    path("terms-conditions/", views.terms_conditions, name="terms-conditions"),
    path("privacy-cookies/", views.privacy_cookies, name="privacy-cookies"),
    # path(r'^workshop-box/$', views.workshop_box, name='workshop-box'),
    path("coc/", views.coc, name="coc"),
    # path(r'^crowdfunding-donors/$', views.crowdfunding_donors, name='crowdfunding-donors'),
    path("server-error/", views.server_error, name="server_error"),

    path('eventnwu/<str:pk>/', views.eventnwu, name="eventnwu"),


    path("form/<slug:step>/", views.organize_form_wizard, name="form_step"),
    path("form/thank_you/", views.form_thank_you, name="form_thank_you"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="core/txt/robots.txt", content_type="text/plain"),
        name="robots",
    ),

    path('home-nwu/', views.home_page, name='home_nwu'),
    path(
        "google3ef9938c7b93b707.html",
        TemplateView.as_view(template_name="google3ef9938c7b93b707.html"),
        name="google_site_verification",
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path('registration-confirmation/<str:pk>/', views.registration_confirmation, name="registration-confirmation"),
    path('project-submission/<str:pk>/', views.project_submission, name="project-submission"),
    path('update-submission/<str:pk>/', views.update_submission, name="update-submission"),
    path('login/', views.login_page, name="login"),
    path('account/', views.account_page, name="account"),
    path('edit-account/', views.edit_account, name="edit-account"),
    #path('request-psw/', views.change_psw, name="change-psw"),
    path('cancel-registration/<uuid:event_uuid>/', views.cancel_registration, name='cancel-registration'),

    path('register/', views.register_page, name="register"),
    path('logout/', views.logout_user, name="logout"),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

