from datetime import datetime
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from ..filters import UpcomingEventsFilter
from ..forms import AddOrganizerForm, EventForm
from ..models import Event, User
from django.core.mail import send_mass_mail
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from django.utils.timezone import now
#-----
geolocator = Nominatim(user_agent="NWU", timeout=5)
import logging
logger = logging.getLogger(__name__)
logger.debug("ADMIN event.py :")
@admin.action(description="Clone selected Events")
def clone_action(modeladmin, request, queryset):
    logger.debug("ADMIN clone_action :")
    logger.debug("ADMIN clone_action : {request}")
    logger.debug("ADMIN clone_action : {queryset}")
    count = 0
    for event in queryset:
        logger.debug("Debugging clone_action.:")
        logger.debug(f"clone duration: {event.duration}")
        logger.debug(f"clone name: {event.name}")
        logger.debug(f"clone id: {event.id}")
        logger.debug(f"clone uuuid: {event.is_on_homepage}")
        event.clone()
        count += 1
    messages.success(request, "{} event{} cloned".format(count, "" if count == 1 else "s"))
#----
geolocator = Nominatim(user_agent="nwu_app")

def latlng_to_address(latlng_str):
    """Convert lat,lng string to human-readable address"""
    if not latlng_str:
        return ""
    try:
        lat, lng = map(float, latlng_str.split(","))
        location = geolocator.reverse((lat, lng), exactly_one=True)
        return location.address if location else latlng_str
    except Exception as e:
        logger.error("Error converting latlng to address: %s", e)
        return latlng_str

def get_upcoming_events_summary_for_group(nwgroup):
    upcoming_events = Event.objects.filter(nwgroup=nwgroup, date__gte=now()).order_by("date")[:5]
    if not upcoming_events:
        return "No upcoming events at the moment."
    return "\n".join(f"- {event.name} on {event.date}" for event in upcoming_events)
def reverse_geocode(latlng):
    """Convert 'lat,lng' string to human-readable address"""
    if not latlng:
        return "Unknown location"
    try:
        lat_str, lng_str = latlng.split(',')
        location = geolocator.reverse((float(lat_str.strip()), float(lng_str.strip())), exactly_one=True, language='en')
        return location.address if location else latlng
    except (ValueError, GeocoderServiceError) as e:
        logger.debug("Reverse geocode failed for %s: %s", latlng, e)
        return latlng
#-----
def get_readable_location(latlng: str) -> str:
    """
    Convert a 'lat,lng' string into a human-readable address.
    Returns a string or 'Unknown Location' if not found.
    """
    if not latlng:
        return "Location not specified"

    try:
        lat, lng = map(float, latlng.split(","))
        geolocator = Nominatim(user_agent="nwu_app")
        location = geolocator.reverse((lat, lng), exactly_one=True, language='en')
        if location:
            return location.address
        return "Location not found"
    except Exception as e:
        logger.error("Error in reverse geocoding for '%s': %s", latlng, str(e))
        return "Location not found"
#----

@admin.action(description="Freeze selected Events")
#__new__
def freeze_action(modeladmin, request, queryset):
    """
    Freeze selected events, making the event website inaccessible as if not yet live,
    and send cancellation email to Group B (participants, main organizer, and team members).
    """
    geolocator = Nominatim(user_agent="nwu_app")
    count = 0

    for event in queryset:
        # Freeze the event
        event.freeze()
        count += 1
        logger.debug("Event frozen: %s", event)

        # Get human-readable location
        location_text = "Location not specified"
        if event.latlng:
            try:
                lat_str, lng_str = event.latlng.split(",")
                location = geolocator.reverse((float(lat_str), float(lng_str)))
                if location:
                    location_text = location.address
            except Exception as e:
                logger.warning("Reverse geocoding failed for %s: %s", event.latlng, e)
                location_text = event.latlng

        # Format event date safely
        if event.date:
            try:
                event_date_str = event.date.strftime("%d %B %Y")
            except AttributeError:
                event_date_str = str(event.date)
        else:
            event_date_str = "Date not specified"

        # Collect recipients (Group B)
        recipients_set = set()
        recipients_set.update(event.participants.all())
        if event.main_organizer:
            recipients_set.add(event.main_organizer)
        recipients_set.update(event.team.all())

        recipients = [u.email for u in recipients_set if u.email]
        logger.debug("Group B (freeze) recipients: %s", recipients)

        if recipients:
            subject = f"Event Cancellation Notice: {event.name}"
            message = (
                f"Dear NWU Member,\n\n"
                f"We regret to inform you that the following event has been canceled:\n\n"
                f"Event: {event.name}\n"
                f"Location: {location_text}\n"
                f"Date: {event_date_str}\n\n"
                f"We apologize for any inconvenience this may cause and truly appreciate your understanding. Thank you for being part of our Nordic Walking community.\n"
                f"In the meantime, please check our upcoming events here: "
                #f"https://nwu.pythonanywhere.com/en/events/\n\n"
                f"https://www.nordicwalkingunited.org/en/events/\n\n"
                f"We look forward to walking with you soon!\n\n"
                f"Best regards,\n"
                f"The Nordic Walking United Event Team"
            )

            datatuple = [(subject, message, 'nordicwalkingunited@gmail.com', [email]) for email in recipients]
            send_mass_mail(datatuple, fail_silently=False)
            logger.debug("Cancellation emails sent to Group B for event: %s", event.name)

    messages.success(request, "{} event{} frozen".format(count, "" if count == 1 else "s"))


#EndNew_____



@admin.action(description="Unfreeze selected events")
def unfreeze_action(modeladmin, request, queryset):
    """
    Unfreeze selected events, making the event website accessible as if it is live,
    and send notification email to Group B (participants, main organizer, and team members).
    """
    geolocator = Nominatim(user_agent="nwu_app")
    count = 0

    for event in queryset:
        # Unfreeze the event
        event.unfreeze()
        count += 1
        logger.debug("Event unfrozen: %s", event)

        # Get human-readable location
        location_text = "Location not specified"
        if event.latlng:
            try:
                lat_str, lng_str = event.latlng.split(",")
                location = geolocator.reverse((float(lat_str), float(lng_str)))
                if location:
                    location_text = location.address
            except Exception as e:
                logger.warning("Reverse geocoding failed for %s: %s", event.latlng, e)
                location_text = event.latlng

        # Format event date safely
        if event.date:
            try:
                event_date_str = event.date.strftime("%d %B %Y")
            except AttributeError:
                event_date_str = str(event.date)
        else:
            event_date_str = "Date not specified"

        # Collect recipients (Group B)
        recipients_set = set()
        recipients_set.update(event.participants.all())
        if event.main_organizer:
            recipients_set.add(event.main_organizer)
        recipients_set.update(event.team.all())

        recipients = [u.email for u in recipients_set if u.email]
        logger.debug("Group B (unfreeze) recipients: %s", recipients)

        if recipients:
            subject = f"Event Now Accessible: {event.name}"
            message = (
                f"Dear NWU Member,\n\n"
                f"We are writing to let you know that the event below has been rescheduled:\n\n"
                f"Event: {event.name}\n"
                f"Location: {location_text}\n"
                f"Date: {event_date_str}\n\n"
                #f"For details on this event, please click on the following link: https://nwu.pythonanywhere.com/en/eventnwu/{event.uuuid}/\n\n"
                f"For details on this event, please click on the following link: https://www.nordicwalkingunited.org/en/eventnwu/{event.uuuid}/\n\n"

                f"We truly appreciate your flexibility and look forward to walking with you soon!\n"
                f"Best regards,\n"
                f"The Nordic Walking United Event Team"
            )

            datatuple = [(subject, message, 'nordicwalkingunited@gmail.com', [email]) for email in recipients]
            #send_mass_mail(datatuple, fail_silently=False)
            logger.debug("Unfreeze emails sent to Group B for event: %s", event.name)

    messages.success(request, "{} event{} unfrozen".format(count, "" if count == 1 else "s"))

def get_readable_address(latlng):
    """
    Converts 'lat,lng' string to human-readable address.
    Returns latlng itself if conversion fails.
    """
    try:
        lat, lng = map(float, latlng.split(","))
        location = geolocator.reverse((lat, lng), timeout=10)
        return location.address if location else latlng
    except Exception as e:
        logger.debug("Geocoding failed for %s: %s", latlng, e)
        return latlng





class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "nwgroup",
        #"is_on_homepage",
        "is_past_event",
        "is_page_live",
        "is_frozen",
        #"email",
        "date",
        "city",
        "country",
        #"preview",
        "start_time",
        "duration",
        "difficulty",
        #"m_difficulty",
        "unit",
        "distance",
        "organizers",

    )

    list_filter = (UpcomingEventsFilter,)
    #search_fields = ("city", "country", "name","nwgroup")
    search_fields = ("nwgroup","country")
    filter_horizontal = ["team"]
    actions = [clone_action, freeze_action, unfreeze_action]
    form = EventForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        logger.debug(f"GET QUERYSET: {qs}")
        logger.debug(f"GET QUERYSET request.user.is_superuser: {request.user.is_superuser}")
        if request.user.is_superuser:
            logger.debug(f"GET QUERYSET qs: {qs}")
            return qs
        logger.debug(f"GET QUERYSET qs.filter(team=request.user): {qs.filter(team=request.user)}")
        return qs.filter(team=request.user)


    @admin.display(
        description=_("past event?"),
        boolean=True,
    )
    def is_past_event(self, obj):
        return not obj.is_upcoming()

    @admin.display(
        description=_("has stats?"),
        boolean=True,
    )
    def has_stats(self, obj):
        return obj.has_stats

#    @admin.display(description=_("page URL"))
#    def full_url(self, obj):
#        url = reverse("core:event", kwargs={"page_url": obj.page_url})
#        url = f"https://djangogirls.org{url}"
#        return mark_safe(f'<a href="{url}">{url}</a>')
    @admin.display(description=_("page URL"))
#    def full_url(self, obj):
#        try:
#            url = reverse("core:eventnwu", kwargs={"pk": obj.uuuid})
#            logger.debug(f"URL: {url}")
#            full_link = f"https://yourdomain.com{url}"  # Replace with actual domain
#            return mark_safe(f'<a href="{full_link}">{full_link}</a>')
#        except NoReverseMatch:
#            return _("URL not available")
    def get_readonly_fields(self, request, obj=None):
        # Superusers can edit all fields
        if request.user.is_superuser:
            return []

        # Moderators: all fields editable except 'nwgroup'
        if request.user.groups.filter(name='Moderators').exists():
            return ['nwgroup']

        # Fallback to default
        return super().get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return [
                (
                    _("Event info"),
                    {
                        "fields": [
                            "name",
                            "date",
                            "city",
                            "country",
                            #"nwgroup",
                            "preview",
                            #"participants",
                            "start_time",
                            "duration",
                            "difficulty",
                            #"m_difficulty",
                            "unit",
                            "distance",
                            "latlng",
                            #"email",
                            #"page_url",
                            #"is_deleted",

                        ]
                    },
                ),
                (_("Event main picture"), {"fields": ["photo", "photo_credit", "photo_link", "is_on_homepage"]}),
                (_("Team"), {"fields": ["main_organizer", "team"]}),
                (
                    _("Event website"),
                    {
                        "fields": [
                            #"page_title",
                            #"page_description",
                            #"page_main_color",
                            #"page_custom_css",
                            "is_page_live",
                        ]
                    },
                ),
                #(
                #    _("Statistics"),
                #    {
                #        "fields": [
                #            "applicants_count",
                #            "attendees_count",
                #        ]
                #    },
                #),
            ]
        return [

            (_("Event info"), {"fields": ["name", "date", "city", "nwgroup", "country", "preview", "start_time","duration","difficulty","unit","distance","latlng"]}),
            #(_("Event info"), {"fields": ["name", "date", "city", "nwgroup", "country", "preview", "start_time","duration","difficulty","m_difficulty","unit","distance","latlng"]}),
            (
                _("Event main picture"),
                {
                    "fields": [
                        "photo",
                        "photo_credit",
                        "photo_link",
                    ]
                },
            ),
            (
                _("Event website"),
                #{"fields": ["page_title", "page_description", "page_main_color", "page_custom_css", "is_page_live"]},
                {"fields": ["is_page_live"]},
            ),
            #(
                #_("Statistics"),
                #{
                    #"fields": [
                        #"applicants_count",
                        #"attendees_count",
                    #]
                #},
            #),
        ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "manage_organizers/",
                self.admin_site.admin_view(self.view_manage_organizers),
                name="core_event_manage_organizers",
            ),
            path(
                "add_organizers/",
                self.admin_site.admin_view(self.view_add_organizers),
                name="core_event_add_organizers",
            ),
        ]
        return my_urls + urls

    def _get_future_events_for_user(self, request):
        """
        Retrieves a list of future events, ordered by name.
        It's based on get_queryset, so superuser see all events, while
        is_staff users see events they're assigned to only.
        """
        return self.get_queryset(request).filter(date__gte=datetime.now().strftime("%Y-%m-%d")).order_by("name")

    def _get_event_from_get(self, request, all_events):
        """
        Retrieves a particular event from request.GET['event_id'], or
        returns the first one from all events available to the user.
        """
        if "event_id" in request.GET:
            try:
                return all_events.get(id=request.GET["event_id"])
            except Event.DoesNotExist:
                pass
        else:
            return all_events.first()

    def view_manage_organizers(self, request):
        """
        Custom admin view that allows user to remove organizers from an event
        """
        all_events = self._get_future_events_for_user(request)
        event = self._get_event_from_get(request, all_events)

        if "remove" in request.GET and event in all_events:
            from core.models import User

            user = User.objects.get(id=request.GET["remove"])
            if user == request.user:
                messages.error(request, _("You cannot remove yourself from a team."))
            elif user in event.team.all():
                event.team.remove(user)
                messages.success(
                    request, _("Organizer %(user_name)s has been removed") % {"user_name": user.get_full_name()}
                )
                return HttpResponseRedirect(reverse("admin:core_event_manage_organizers") + f"?event_id={event.id}")

        return render(
            request,
            "admin/core/event/view_manage_organizers.html",
            {
                "all_events": all_events,
                "event": event,
                "title": _("Remove organizers"),
            },
        )

    def view_add_organizers(self, request):
        """
        Custom admin view that allows user to add new organizer to an event
        """
        all_events = self._get_future_events_for_user(request)
        event = self._get_event_from_get(request, all_events)

        if request.method == "POST":
            form = AddOrganizerForm(request.POST, event_choices=all_events)
            if form.is_valid():
                user = form.save()
                messages.success(
                    request,
                    _(
                        "%(user_name)s has been added to your event, yay! They've been also"
                        " invited to Slack and should receive credentials to login"
                        " in an e-mail."
                    )
                    % {"user_name": user.get_full_name()},
                )
                return redirect("admin:core_event_add_organizers")
        else:
            form = AddOrganizerForm(event_choices=all_events)

        return render(
            request,
            "admin/core/event/view_add_organizers.html",
            {
                "all_events": all_events,
                "event": event,
                "form": form,
                "title": _("Add organizers"),
            },
        )




    #def save_model(self, request, obj, form, change):
        #logger.debug("ADMIN save_model obj: %s", obj)
        #logger.debug("ADMIN save_model request: %s", request)
        #logger.debug("ADMIN save_model change: %s", change)

#____________________________________________________________________________________

    def has_add_permission(self, request):
        # Disable "Add Event" for all users
        return False
#NEW NEW NEW
    tracked_fields = [
        "date", "preview", "start_time", "duration",
        "difficulty", "distance", "is_on_homepage", "is_page_live", "latlng"
    ]


    def save_model(self, request, obj, form, change):
        logger.debug("=== ENTER save_model ===")
        logger.debug("ADMIN save_model obj: %s", obj)
        logger.debug("ADMIN save_model change: %s", change)

        changed_fields = []
        old_obj = None

        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            for field in self.tracked_fields:
                old_value = getattr(old_obj, field)
                new_value = getattr(obj, field)
                if old_value != new_value:
                    # Convert latlng to human-readable address for email
                    if field == "latlng":
                        old_value = latlng_to_address(old_value)
                        new_value = latlng_to_address(new_value)
                    changed_fields.append((field, old_value, new_value))

        # Save object first
        super().save_model(request, obj, form, change)
        logger.debug("Object saved.")

        # --- Group A: New live event ---
        # --- Group A: New live event ---
        # --- Group A: New live event ---
        if obj.is_page_live and (not change or (change and not getattr(old_obj, "is_page_live", False))):
            total_in_group = self.model.objects.filter(nwgroup=obj.nwgroup).count()

    # --- Case 1: FIRST and ONLY event in this group -> Group C email ONLY ---

# --- Case 1: FIRST and ONLY event in this group -> Group C email ONLY ---
            if total_in_group == 1:
    # Collect only main organizers from ACTIVE (live) groups
                main_org_ids = (
                    self.model.objects
                    .filter(is_page_live=True)                # only groups that already have live events
                    .exclude(main_organizer__isnull=True)
                    .values_list("main_organizer", flat=True)
                    .distinct()
                )
                recipients_qs = User.objects.filter(id__in=main_org_ids).only("id", "first_name", "email")
                recipients = [u for u in recipients_qs if u.email]

                if recipients:
                    subject = f"New NWU Group and First Event Live: {obj.nwgroup}"
                    #event_url = f"https://nwu.pythonanywhere.com/en/eventnwu/{obj.uuuid}/"
                    event_url = f"https://www.nordicwalkingunited.org/en/eventnwu/{obj.uuuid}/"
                    address = latlng_to_address(obj.latlng)
                    message = (
                        f"Dear Organizer,\n\n"
                        f"The new NWU group '{obj.nwgroup}' in {obj.city}, {obj.country} has been approved, "
                        f"and its first event '{obj.name}' on {obj.date} has just gone live!\n\n"
                        f"Location: {address}\n\n"
                        f"Check the event page: {event_url}\n\n"
                        f"Best regards,\nNordic Walking United Team"
                    )
                    datatuple = [(subject, message, 'nordicwalkingunited@gmail.com', [u.email]) for u in recipients]
                    send_mass_mail(datatuple, fail_silently=False)
                    logger.debug("Group C (main organizers of active groups) notified: %s", [u.email for u in recipients])

    # stop here so the regular "New Event Live" email isn't also sent
                return



    # --- Case 2: Existing group → send normal “New Event Live” email (Group A) ---
            else:
                related_events = self.model.objects.filter(nwgroup=obj.nwgroup)
                user_set = set()
                for event in related_events:
                    user_set.update(event.participants.all())
                if event.main_organizer:
                    user_set.add(event.main_organizer)
                if hasattr(event, "team"):
                    user_set.update(event.team.all())
                recipients = [u for u in user_set if u.email]

                summary = get_upcoming_events_summary_for_group(obj.nwgroup)

                datatuple = []
                for user in recipients:
                    subject = f"New Event Live: {obj.name} in {obj.nwgroup}"
                    #event_url = f"https://nwu.pythonanywhere.com/en/eventnwu/{obj.uuuid}/"
                    event_url = f"https://www.nordicwalkingunited.org/en/eventnwu/{obj.uuuid}/"
                    message = (
                        f"Dear {user.first_name},\n\n"
                        f"The event '{obj.name}' on {obj.date} in the '{obj.nwgroup}' group has just gone live!\n"
                        f"Location: {latlng_to_address(obj.latlng)}\n\n"
                        f"Check the event page: {event_url}\n\n"
                        f"Upcoming events in your NWGroup:\n{summary}\n\n"
                        f"Best regards,\nNordic Walking United Team"
                    )
                    datatuple.append((subject, message, 'nordicwalkingunited', [user.email]))

                if datatuple:
                    send_mass_mail(datatuple, fail_silently=False)
                    logger.debug("Group A (existing group) notifications sent to %s", [u.email for u in recipients])

#########################################################################################################################
# --- Group B: Updated event ---
        elif change and changed_fields and obj.is_page_live:
            user_set = set(obj.participants.all())
            if obj.main_organizer:
                user_set.add(obj.main_organizer)
            if hasattr(obj, "team"):
                user_set.update(obj.team.all())
            recipients = [u for u in user_set if u.email]

            summary = get_upcoming_events_summary_for_group(obj.nwgroup)

            changes_summary = "\n".join(
                f"• {field}: '{old}' → '{new}'" for field, old, new in changed_fields if field != "preview"
            )

            datatuple = []
            for user in recipients:
                subject = f"Update on Event '{obj.name}' in {obj.nwgroup}"
                #event_url = f"https://nwu.pythonanywhere.com/en/eventnwu/{obj.uuuid}/"
                event_url = f"https://www.nordicwalkingunited.org/en/eventnwu/{obj.uuuid}/"
                message = (
                    f"Dear {user.first_name},\n\n"
                    f"The NWU event '{obj.name}' on {obj.date} in your group '{obj.nwgroup}' has been updated.\n"
                    f"Location: {latlng_to_address(obj.latlng)}\n\n"
                    f"Changes:\n{changes_summary}\n\n"
                    f"Check the event page: {event_url}\n\n"
                    f"Upcoming events in your NWGroup:\n{summary}\n\n"
                    f"Best regards,\nNordic Walking United Team"
                )
                datatuple.append((subject, message, 'nordicwalkingunited@gmail.com', [user.email]))

            if datatuple:
                send_mass_mail(datatuple, fail_silently=False)
                logger.debug("Group B notifications sent to %s", [u.email for u in recipients])


# --- Handle m2m changes safely ---
@receiver(m2m_changed, sender=Event.team.through)
def handle_team_member_changes(sender, instance, action, pk_set, **kwargs):
    if action not in ["post_add", "post_remove"]:
        return

    added = action == "post_add"
    removed = action == "post_remove"
    user_objs = User.objects.filter(pk__in=pk_set)
    logger.debug("Team member change detected. Added: %s, Removed: %s", added, removed)

    # Prevent recursion
    m2m_changed.disconnect(handle_team_member_changes, sender=Event.team.through)
    try:
        # Update team in all FUTURE events in same NWGroup
        related_events = Event.objects.future().filter(nwgroup=instance.nwgroup).exclude(pk=instance.pk)
        for event in related_events:
            if added:
                event.team.add(*user_objs)
            if removed:
                event.team.remove(*user_objs)
    finally:
        m2m_changed.connect(handle_team_member_changes, sender=Event.team.through)

    # Notify all users of the event (participants + main organizer + team)
    all_users_set = set(instance.participants.all())
    if instance.main_organizer:
        all_users_set.add(instance.main_organizer)
    all_users_set.update(instance.team.all())

    recipients = [u for u in all_users_set if u.email]
    if not recipients:
        logger.debug("No recipients found for team member change.")
        return

    summary = get_upcoming_events_summary_for_group(instance.nwgroup)
    #action_text = "added to" if added else "removed from"
    #if added:
    #    action_sentence = "have been added as an organizer"
    #else:
    #    action_sentence = "are no longer listed as an organizer"

    if added:
        action_sentence = "have been added as an organizer"
        thank_you_line = ""
    else:
        action_sentence = "are no longer listed as an organizer"
        thank_you_line = (
            "\n\nWe sincerely thank them for the time, care, and energy they’ve "
            "contributed to this group and to the Nordic Walking United community."
        )

    changed_names = ", ".join(u.get_full_name() for u in user_objs)

    datatuple = []
    for user in recipients:
        subject = f"Organizers Update - {instance.nwgroup}"
        event_url = f"https://www.nordicwalkingunited.org/en/home-nwu/"

        message = (
            f"Dear {user.first_name},\n\n"
            f"We’d like to let you know that {changed_names} {action_sentence} "
            f"for the  “{instance.nwgroup}” group.\n\n"
            f"{thank_you_line}\n\n"


    f"We truly appreciate the time, care, and energy you bring to your group and to the global NWU community.\n\n"
    "To help us maintain a safe, respectful, and transparent environment for everyone, "
    "we kindly ask that all team members review and agree to the Nordic Walking United (NWU) "
    "Terms of Service, Privacy Policy, Photo & Media Release, and Code of Conduct before "
    "creating, managing, or participating in any NWU events or group activities.\n\n"
    "You can find these important documents here:\n\n"
    "Terms & Policies:\n"
    "https://www.nordicwalkingunited.org/en/nwu-rules/\n\n"

    "Code of Conduct:\n"
    "https://www.nordicwalkingunited.org/en/coc/\n\n"
            "With warm regards,\n"
            "Nordic Walking United 🌿"
        )

        datatuple.append((subject, message, 'nordicwalkingunited@gmail.com', [user.email]))

    if datatuple:
        send_mass_mail(datatuple, fail_silently=False)
        logger.debug("Team member change notifications sent to %s", [u.email for u in recipients])
#END NEW
