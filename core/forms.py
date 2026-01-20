from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django_countries import countries
from django.conf import settings
from django.core.validators import validate_email
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django_date_extensions.fields import ApproximateDateFormField
from django_countries.fields import LazyTypedChoiceField
from django.forms import ModelForm
from .models import Event, User,  Submission
from django_ckeditor_5.widgets import CKEditor5Widget
from django_resized import ResizedImageField
from django.forms.widgets import SplitDateTimeWidget
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

import logging
from core.validators import (
    validate_approximatedate,
    validate_event_date,
    validate_future_date,
)
logger = logging.getLogger(__name__)
"""
class SubmissionForm(forms.ModelForm):
    class Meta:
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["preview"].required = False
    class Meta:
        model = Submission
        fields = ['details','preview']
        widgets = {
              "preview": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="default"
               )

        }
"""

class BetterReCaptchaField(ReCaptchaField):
    """A ReCaptchaField that always works in DEBUG mode"""

    def clean(self, values):
        if settings.DEBUG:
            return values[0]
        return super().clean(values)


class AddOrganizerForm(forms.Form):
    """
    Custom form for adding new organizers to an existing event.

    If user of given email already exists, they're added to the event and
    receive e-mail notification about it.

    If user is new, they're created (randomly generated password), invited
    to Slack and receive e-mail notification with instructions to login
    (including password).
    """

    event = forms.ModelChoiceField(queryset=Event.objects.all())
    name = forms.CharField(label=_("Organizer's first and last name"))
    email = forms.CharField(label=_("E-mail address"), validators=[validate_email])

    def __init__(self, *args, **kwargs):
        event_choices = kwargs.pop("event_choices", None)
        super().__init__(*args, **kwargs)
        if event_choices is not None:
            self.fields["event"].queryset = event_choices

    def save(self, *args, **kwargs):
        assert self.is_valid()
        self._errors = []
        email = self.cleaned_data["email"]
        event = self.cleaned_data["event"]
        first_name, _, last_name = self.cleaned_data["name"].partition(" ")
        user = event.add_organizer(email, first_name, last_name)
        return user


class EventChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.city}, {obj.country}, {obj.nwgroup},"





class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["nwgroup","city", "country", "date","preview", "participants","start_time", "difficulty", "unit", "distance", "email", "latlng", "name"]
        #fields = ["nwgroup","city", "country", "date","preview", "participants","start_time", "difficulty", "unit", "distance", "email", "latlng", "name", "page_title", "page_url"]

    @transaction.atomic
    def save(self, commit=True):
        """Save the event and create default content in case of new instances"""
        created = not self.instance.pk
        instance = super().save(commit=commit)
        if commit and created:
            # create default content
            instance.add_default_content()
            instance.add_default_menu()

        return instance
class BaseOrganizerFormSet(forms.BaseFormSet):
    def get_data_for_saving(self):
        organizers = [form.cleaned_data for form in self.forms if form.has_changed()]
        main_organizer = organizers.pop(0)
        data = {
            "email": main_organizer["email"],
#            "first_name": main_organizer["first_name"],
#            "last_name": main_organizer["last_name"],
#            "coorganizers": organizers,
        }
        return data


class OrganizerForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "compact-input"}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "compact-input"}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={"class": "compact-input"}))


OrganizersFormSet = forms.formset_factory(
    OrganizerForm, formset=BaseOrganizerFormSet, extra=1, max_num=10, min_num=1, validate_min=True
)


class WorkshopForm(forms.Form):
#    fields = ["nwgroup","city", "country", "date", "email", "latlng", "name", "page_title", "page_url"]

    date = ApproximateDateFormField(widget=forms.TextInput(attrs={"class": "compact-input"}))
    city = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={"class": "compact-input"}))
    nwgroup = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={"class": "compact-input"}))
    #captcha = ReCaptchaField(widget=ReCaptchaV3Checkbox) # or ReCaptchaV3, ReCaptchaV2Invisible
    country = LazyTypedChoiceField(choices=[(None, _("Choose country")), *list(countries)])

    def clean_date(self):
        date = self.cleaned_data.get("date")
        logger.debug("WorkshopForm date: %s", date)
        validate_approximatedate(date)
        # Check if the event is in the future
        try:
            validate_future_date(date)
        except ValueError:
            return ValueError(_("Please enter a valid date, which is at least 1 day from now."))
        # Check if date is 3 months away
        validate_event_date(date)
        return date

    def get_data_for_saving(self):
        return self.cleaned_data





#class CustomUserCreateForm(UserCreationForm):
#    class Meta:
#        model = User
#        fields = ['username', 'email', 'name', 'password1', 'password2']
#        widgets = {
#            'username': forms.TextInput(attrs={'class':'form-field--input'}),
#            'name':forms.TextInput(attrs={'class':'form-field--input'}),
#            'email':forms.EmailInput(attrs={'class':'form-field--input'}),

#        }
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['details', 'imgpresent']



class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'email',  'password1', 'password2','name', 'last_name','address','country_user', 'age_range', 'bio']

        country_user = LazyTypedChoiceField(choices=[(None, _("Choose country")), *list(countries)])

        age_range = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-field--input'}),
            'email': forms.EmailInput(attrs={'class': 'form-field--input'}),
            'name': forms.TextInput(attrs={'class': 'form-field--input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-field--input'}),
            'address': forms.TextInput(attrs={'class': 'form-field--input'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-field--input-txarea',
                'rows': 6,
                'style': 'min-height:160px; width:100%;',
            }),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _(
                    "This email address is already registered 💚\n"
                    "Please log in instead, or use a different email."
                )
            )
        return email

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _(
                    "This email address is already registered 💚\n"
                    "Please log in instead, or use a different email."
                )
            )
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make fields required
        self.fields['last_name'].required = True
        self.fields['country_user'].required = True
        self.fields['address'].required = True
class UserForm(forms.ModelForm):
    country_user = LazyTypedChoiceField(
        choices=[(None, _("Choose country")), *list(countries)]
    )

    class Meta:
        model = User
        fields = [
            'avatar', 'username', 'email',
            'name', 'last_name', 'address',
            'country_user', 'age_range', 'bio'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-field--input'}),
            'email': forms.EmailInput(attrs={'class':'form-field--input'}),
            'name': forms.TextInput(attrs={'class':'form-field--input'}),
            'last_name': forms.TextInput(attrs={'class':'form-field--input'}),
            'address': forms.TextInput(attrs={'class':'form-field--input'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-field--input-txarea',
                'rows': 6,
                'style': 'min-height:160px;',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make fields required
        self.fields['last_name'].required = True
        self.fields['country_user'].required = True
        self.fields['address'].required = True


class EventRegisterForm(forms.Form):
    confirm = forms.BooleanField(label="I want to join as a Participant")




