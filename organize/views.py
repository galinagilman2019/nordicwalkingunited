from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from formtools.wizard.views import NamedUrlSessionWizardView

from core.models import User
#from django.contrib.auth.models import Group
from .emails import send_application_confirmation, send_application_notification
from .forms import (
    ApplicationForm,
    OrganizersFormSet,
    PreviousEventForm,
    RemoteWorkshopForm,
    WorkshopForm,
    WorkshopTypeForm,
)
from .models import EventApplication
from core.models.nwu_manual import NWU_Manual
# ORGANIZE FORM #

import logging

logger = logging.getLogger(__name__)




FORMS = (
    ("previous_event", PreviousEventForm),
    ("application", ApplicationForm),
    ("organizers", OrganizersFormSet),
    ("workshop_type", WorkshopTypeForm),
    ("workshop", WorkshopForm),
    ("workshop_remote", RemoteWorkshopForm),
)

TEMPLATES = {
    "previous_event": "organize/form/step1_previous_event.html",
    "application": "organize/form/step2_application.html",
    "organizers": "organize/form/step3_organizers.html",
    "workshop_type": "organize/form/step4_workshop_type.html",
    "workshop": "organize/form/step5_workshop.html",
    "workshop_remote": "organize/form/step5_workshop_remote.html",
}

#class reMapStart(forms.Form):
#    location = forms.CharField()
#    CHOICES = [(x, x) for x in ("cars", "bikes")]
#    technology = forms.ChoiceField(choices=CHOICES)

#class reMapLocationConfirmation(forms.Form):

#   def __init__(self, user, *args, **kwargs):
#       super(reMapLocationConfirmation, self).__init__(*args, **kwargs)
#       self.fields['locations'] = forms.ChoiceField(widget=RadioSelect(), choices=[(x, x)  for x in location])

#class reMapData(forms.Form):
#   capacity = forms.IntegerField()

#class reMapWizard(FormWizard):

#    def render_template(self, request, form, previous_fields, step, context=None):
#        if step == 1:
#            location = request.POST.get('0-location')
#            address, lat, lng, country = getLocation(location)
#            form.fields['locations'] = forms.ChoiceField(widget=RadioSelect(), choices = [])
#            form.fields['locations'].choices = [(x, x) for x in address]
#        return super(reMapWizard, self).render_template(request, form, previous_fields, step, context)

class OrganizeFormWizard(NamedUrlSessionWizardView):
    def get_template_names(self):
        step = self.steps.current
        logger.debug(f"OrganizeFormWizard – rendering step: {step}")
        return [TEMPLATES[step]]
    def done(self, form_list, **kwargs):
        logger.debug("OrganizeFormWizard Entering the 'done' method.")
        data_dict = {}
        for form in form_list:
            data_dict.update(form.get_data_for_saving())
        organizers_data = data_dict.pop("coorganizers", [])
        logger.info(f"Extracted organizers_data: {organizers_data}")

        try:
            application = EventApplication.objects.create(**data_dict)
            logger.info(f"Created application: {application}")

            for organizer in organizers_data:
                application.coorganizers.create(**organizer)
                try:
                    user = User.objects.get(email=organizer["email"])
                    if user.is_blacklisted:
                        application.organizer_blacklisted = True
                        application.save()
                        logger.warning(f"Organizer {user.email} is blacklisted.")
                except User.DoesNotExist:
                    logger.info(f"No user found with email: {organizer['email']}")

            send_application_confirmation(application)
            send_application_notification(application)

            # Store main organizer info + application id in session
            self.request.session["main_organizer_email"] = data_dict.get("main_organizer_email", "")
            self.request.session["main_organizer_first_name"] = data_dict.get("main_organizer_first_name", "")
            self.request.session["application_id"] = application.id

        except ValidationError as error:
            messages.error(self.request, error.messages[0])
            return redirect("organize:prerequisites")

        logger.debug("Exiting 'done' method.")
        return redirect("organize:form_thank_you")


def skip_application_if_organizer(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("previous_event") or {}
    return not cleaned_data.get("has_organized_before")


def skip_workshop_if_remote(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("workshop_type") or {}
    return not cleaned_data.get("remote")


def skip_workshop_remote_if_in_person(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("workshop_type") or {}
    return cleaned_data.get("remote", False)


organize_form_wizard = OrganizeFormWizard.as_view(
    FORMS,
    condition_dict={
        "application": skip_application_if_organizer,
        "workshop": skip_workshop_if_remote,
        "workshop_remote": lambda wizard: False,  # Always skip
        "workshop_type": lambda wizard: False,    # Always skip
    },
    url_name="organize:form_step",
)

# ORGANIZE FORM #

def form_thank_you(request):
    logger.debug("Rendering thank you page.")

    email = request.session.get("main_organizer_email", "")
    first_name = request.session.get("main_organizer_first_name", "")

    return render(
        request,
        "organize/form/thank_you.html",
        {
            "main_organizer_email": email,
            "main_organizer_first_name": first_name,
        }
    )

def index(request):
    return render(request, "organize/index.html", {})


def commitment(request):
    return render(request, "organize/commitment.html", {})


def prerequisites(request):
    """
    Prerequisites step before starting the organize wizard.
    We resolve specific NWU_Manual pages by slug so we can link
    directly to the correct tutorials/handbook pages.
    """

    def get_manual(slug):
        return NWU_Manual.objects.filter(slug=slug).first()

    manuals = {
        # 🔹 Update these slugs to match what you have in the admin

        "organizers_tutorial":            get_manual("organizers-tutorial"),         # intro for organizers
        "the_event_is_ready_for_public_viewing":       get_manual("the-event-is-ready-for-public-viewing"),    # how to organize, step-by-step
        "application_accepted": get_manual("application-accepted"),   # application accepted guide
    }

    return render(request, "organize/prerequisites.html", {
        "manuals": manuals,
    })



def suspend(request):
    return render(request, "organize/suspend.html", {})


def event_funding(request):
    return render(request, "organize/event_funding.html", {})


def slack(request):
    return render(request, "organize/slack.html")
