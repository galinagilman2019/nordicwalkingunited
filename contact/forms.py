# contact/forms.py
from django import forms
from contact.models import ContactEmail


class ContactForm(forms.Form):
    CONTACT_TYPE_CHOICES = [
        (ContactEmail.QUESTION, "Nordic Walking United Local Organizers"),
        (ContactEmail.SUPPORT, "Nordic Walking United (Support Team)"),
    ]

    name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Your full name"}),
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
    )
    contact_type = forms.ChoiceField(
        choices=CONTACT_TYPE_CHOICES,
        label="Who do you want to contact?",
        widget=forms.RadioSelect,
    )
    event = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Select your local group/event",
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Required when contacting Local Organizers.",
    )
    message = forms.CharField(
        label="Your Message",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Type your message here..."}),
    )

    def clean(self):
        cleaned = super().clean()
        contact_type = cleaned.get("contact_type")
        event = cleaned.get("event")

        if contact_type == ContactEmail.QUESTION and not event:
            self.add_error("event", "Please select your group/event when contacting Local Organizers.")
        return cleaned










"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django_bleach.forms import BleachField
from core.models import Event
from contact.models import ContactEmail


class EventChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Display as "City - Date - NW group" for the dropdown
        return f"{obj.city} - {obj.date} - {obj.nwgroup}"  # nwgroup is string


class ContactForm(forms.ModelForm):
    event = EventChoiceField(
        queryset=Event.objects.none(),  # will be set dynamically in view
        required=False,
        label=_("Select upcoming Nordic Walking United event"),
    )
    message = BleachField()

    class Meta:
        model = ContactEmail
        fields = ("name", "email", "contact_type", "event", "message")
        widgets = {"contact_type": forms.RadioSelect}

    def clean_event(self):
        contact_type = self.cleaned_data.get("contact_type")
        event = self.cleaned_data.get("event")
        # Require event if contacting Local Organizer
        if contact_type == ContactEmail.CHAPTER and not event:
            raise forms.ValidationError(_("Please select the event"))
        return event
"""