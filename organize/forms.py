from django import forms
from django.utils import formats
from django.utils.translation import gettext_lazy as _
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField
from django_date_extensions.fields import ApproximateDateFormField
from core.validators_nwu.event_validators import validate_nwgroup
from core.models import Event
from core.validators import (
    validate_approximatedate,
    validate_event_date,
    validate_future_date,
)
import logging
logger = logging.getLogger('djangogirls')
from .constants import INVOLVEMENT_CHOICES

PREVIOUS_ORGANIZER_CHOICES = (
    (True, _("Yes, I've organized a Nordic Walking Group with NWU before")),
    (False, _("No, this is my first time organizing a Nordic Walking Group with NWU")),
)

WORKSHOP_CHOICES = ((True, _("Remote")), (False, _("In-Person")))


class PreviousEventForm(forms.Form):
    has_organized_before = forms.TypedChoiceField(
        coerce=lambda x: x in ["True", True],
        widget=forms.RadioSelect,
        choices=PREVIOUS_ORGANIZER_CHOICES,
        required=True,
    )

    previous_event = forms.ModelChoiceField(
        #queryset=Event.objects.nwg_distinct(),
        queryset=Event.objects.public(),
#        queryset=Event.objects.nwg_distinct(),
#        queryset=Event.objects.public().values_list('nwgroup', flat=True),
#        queryset=Event.objects.public().distinct('nwgroup'),#Not right one from GPT
        empty_label=_("Choose event"),
        required=False,
        widget=forms.Select(attrs={"aria-label": _("Choose event"), "class": "linked-select"}),
    )

    def clean(self):
        has_organized_before = self.cleaned_data.get("has_organized_before")
        previous_event = self.cleaned_data.get("previous_event")
        logger.debug("Form has_organized_before: %s", has_organized_before)
        logger.debug("Form previous_event: %s", previous_event)
        #if has_organized_before is True and not previous_event:
            #self.add_error("has_organized_before", _("You have to choose an event."))

        return self.cleaned_data
    #logger.warning("has_organized_before",has_organized_before)
    #logger.warning("previous_event",previous_event)
    def get_data_for_saving(self):
        data = self.cleaned_data
        # Clean the previous event if someone filled it
        # and marked themselves as first-time organizers
        if not data["has_organized_before"]:
            data["previous_event"] = None
        del data["has_organized_before"]
        return data



class ApplicationForm(forms.Form):
    about_you = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    why = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    involvement = forms.MultipleChoiceField(choices=INVOLVEMENT_CHOICES, widget=forms.CheckboxSelectMultiple)
    experience = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))

    def get_data_for_saving(self):
        data = self.cleaned_data
        data["involvement"] = ", ".join(data.get("involvement"))
        return data


class BaseOrganizerFormSet(forms.BaseFormSet):
    def get_data_for_saving(self):
        organizers = [form.cleaned_data for form in self.forms if form.has_changed()]
        main_organizer = organizers.pop(0)
        data = {
            "main_organizer_email": main_organizer["email"],
            "main_organizer_first_name": main_organizer["first_name"],
            "main_organizer_last_name": main_organizer["last_name"],
            "coorganizers": organizers,
        }
        return data


class OrganizerForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "compact-input"}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "compact-input"}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={"class": "compact-input"}))


OrganizersFormSet = forms.formset_factory(
    OrganizerForm, formset=BaseOrganizerFormSet, extra=1, max_num=10, min_num=1, validate_min=True
)


from django import forms


class WorkshopForm(forms.Form):
    date = forms.DateField(
        widget=forms.TextInput(attrs={
            "class": "compact-input",
            "placeholder": "21 Dec 2025",
            "title": "Please enter the date in the format: Day Abbreviated Month Year (e.g., 21 Dec 2025)"
        }),
        input_formats=["%d %b %Y"],  # Accepting format "21 Dec 2025"
    )
    city = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={"class": "compact-input"}))
    nwgroup = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={"class": "compact-input"}))
    country = LazyTypedChoiceField(choices=[(None, _("Choose country")), *list(countries)])
    venue = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    #sponsorship = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    additional = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))

    logger.debug("ORGANIZE WORKSHOPFORMForm : %s")

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        nwgroup = cleaned_data.get("nwgroup")

        logger.debug("WorkshopForm clean() - date: %s", date)
        logger.debug("WorkshopForm clean() - nwgroup: %s", nwgroup)

        if nwgroup:
            try:
                validate_nwgroup(nwgroup)
            except ValueError:
                self.add_error("nwgroup", _("Please enter a unique group name."))

        if date:
            try:
                validate_approximatedate(date)
                validate_future_date(date)
                validate_event_date(date)
            except ValueError:
                self.add_error("date", _("Please enter a valid future date, at least 3 months away."))

        return cleaned_data

    def get_data_for_saving(self):
        return self.cleaned_data



class RemoteWorkshopForm(forms.Form):
    date = ApproximateDateFormField(widget=forms.TextInput(attrs={"class": "compact-input"}))
    city = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={"class": "compact-input"}))
    country = LazyTypedChoiceField(choices=[(None, _("Choose country")), *list(countries)])
    sponsorship = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    coaches = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    tools = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    diversity = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))
    additional = forms.CharField(widget=forms.Textarea(attrs={"class": "compact-input"}))

    def clean_date(self):
        date = self.cleaned_data.get("date")
        validate_approximatedate(date)
        # Check if the event is in the future
        validate_future_date(date)
        # Check if date is 3 months away
        validate_event_date(date)
        return date

    def get_data_for_saving(self):
        return self.cleaned_data


class WorkshopTypeForm(forms.Form):
    remote = forms.TypedChoiceField(
        coerce=lambda x: x in ["True", True], widget=forms.RadioSelect, choices=WORKSHOP_CHOICES, required=True
    )

    def get_data_for_saving(self):
        return self.cleaned_data
