
from django.urls import path
from .views import contact_view, contact_success_view

app_name = 'contact'

urlpatterns = [
    path('contact/', contact_view, name='contact_form'),

    path('contact/success/', contact_success_view, name='contact_success'),
]