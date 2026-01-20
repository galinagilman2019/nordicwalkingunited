from django.template.loader import render_to_string

from core.emails import send_email
from django.contrib.auth import get_user_model
User = get_user_model()

def send_application_confirmation(event_application):
    #subject = f"Application Submitted for Organizing  {event_application.nwgroup} in {event_application.city} {event_application.country
    subject = f"Application Submitted for Organizing  NWU group '{event_application.nwgroup}' in {event_application.city} {event_application.country}"
    # Get the list of organizers and coorganizers
    organizers_data = event_application.coorganizers.all()

    # Prepare the list of organizers with first name, last name, and email
    organizers_list = [
        {
            "first_name": organizer.first_name,
            "last_name": organizer.last_name,
            "email": organizer.email
        }
        for organizer in organizers_data
    ]
    content = render_to_string(
        "emails/organize/application_confirmation.html",
        {
            "city": event_application.city,
            "group": event_application.nwgroup,
            "country": event_application.country,
            "organizers": organizers_list,
            "organizer_email": event_application.main_organizer_email,
            "organizer_first_name": event_application.main_organizer_first_name,
            "organizer_last_name": event_application.main_organizer_last_name,
        },
    )
    send_email(content, subject, event_application.get_organizers_emails())

def send_application_notification(event_application):
    """
    Triggered when user submits application to organize new Nordic Walk United event
    Sent to hello@djangogirls.org as a notification with reply-to to organizers
    who applied
    """
    subject = (
        f"New request to organise NWU {event_application.nwgroup} in  {event_application.city}, {event_application.get_country_display()}"
    )
    content = render_to_string(
        "emails/organize/application_notification.html",
        {
            "application": event_application,
        },
    )

    #send_email(content, subject, ["nordicwalkingunited@gmail.com"], reply_to=[event_application.get_main_organizer_email()])
    # All active superusers
    superusers = list(
        User.objects.filter(is_superuser=True, is_active=True)
        .values_list("email", flat=True)
    )

    # Ensure main inbox is included
    admin_inbox = "nordicwalkingunited@gmail.com"
    if admin_inbox not in superusers:
        superusers.append(admin_inbox)

    # Remove any empty emails
    superusers = [email for email in superusers if email]

    send_email(
        content,
        subject,
        superusers,
        reply_to=[event_application.get_main_organizer_email()],
    )

def send_application_deployed_email(event_application, event, email_password):
    #subject = f"Congrats! Your application to organize NWU group {event_application.nwgroup} in  {event_application.city} has been accepted!"
    subject = f"Congratulations on Your Accepted Application to Organize an NWU Group!"
    organizers_data = event_application.coorganizers.all()

    # Prepare the list of organizers with first name, last name, and email
    organizers_list = [
        {
            "first_name": organizer.first_name,
            "last_name": organizer.last_name,
            "email": organizer.email
        }
        for organizer in organizers_data
    ]
    content = render_to_string(
        "emails/organize/event_deployed.html",
        {

            "city": event_application.city,
            "group": event_application.nwgroup,
            "country": event_application.country,
            "organizers": organizers_list,
            "organizer_email": event_application.main_organizer_email,
            "organizer_first_name": event_application.main_organizer_first_name,
            "organizer_last_name": event_application.main_organizer_last_name,
        },
    )
    #

    recipients = event_application.get_organizers_emails()
    #recipients.append(event.email)  # add event's djangogirls.org email
    send_email(content, subject, recipients)


def send_application_rejection_email(event_application):
    """Sends a rejection email to all organizers who created this application"""
    subject = f"Application to organize NWU {event_application.nwgroup} in {event_application.city} has been reviewed"
    content = render_to_string("emails/organize/rejection.html", {"application": event_application})
    send_email(content, subject, event_application.get_organizers_emails())
