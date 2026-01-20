import json
import logging
import smtplib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.utils.timezone import now

from core.models import Event
from contact.models import ContactEmail
from .forms import ContactForm

logger = logging.getLogger(__name__)
User = get_user_model()

# TEMP codes you can treat as "mail server deferred delivery"
TEMP_SMTP_CODES = {450, 451, 452, 421}


def contact_success_view(request):
    return render(request, "contact/contact_success.html")


def contact_view(request):
    today = now().date()

    # ✅ Only READY + UPCOMING events
    upcoming_events_qs = (
        Event.objects.filter(
            is_page_live=True,
            date__gte=today,
        )
        .order_by("nwgroup", "city", "date")
    )

    upcoming_events = [
        {
            "id": e.id,
            "city": e.city,
            "date": str(e.date),
            "nwgroup": e.nwgroup,
            "country": getattr(e, "country", "") or "",
        }
        for e in upcoming_events_qs
    ]
    upcoming_events_json = json.dumps(upcoming_events)

    if request.method == "POST":
        form = ContactForm(request.POST)
        form.fields["event"].queryset = upcoming_events_qs

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            contact_type = form.cleaned_data["contact_type"]
            event = form.cleaned_data.get("event")
            message = form.cleaned_data["message"]

            audience_label = (
                "Nordic Walking United Local Organizers"
                if contact_type == ContactEmail.QUESTION
                else "Nordic Walking United (Support Team)"
            )

            # -------------------- Recipients --------------------
            if contact_type == ContactEmail.QUESTION:
                team_emails = list(event.team.all().values_list("email", flat=True)) if event else []
                if not team_emails:
                    team_emails = [
                        getattr(settings, "DEFAULT_CONTACT_EMAIL", None)
                        or getattr(settings, "EMAIL_HOST_USER", None)
                    ]
            else:
                team_emails = list(User.objects.filter(is_superuser=True).values_list("email", flat=True))
                if not team_emails:
                    team_emails = [
                        getattr(settings, "DEFAULT_CONTACT_EMAIL", None)
                        or getattr(settings, "EMAIL_HOST_USER", None)
                    ]

            team_emails = sorted({addr for addr in team_emails if addr})

            if not team_emails:
                logger.error("CONTACT: No recipients resolved (team_emails empty).")
                messages.error(request, "❌ No recipients found. Please try again later.")
                return redirect("contact:contact")

            # -------------------- Email content --------------------
            email_subject = f"[Contact • {audience_label}] from {name}"
            email_body = (
                "--- Nordic Walking United Contact Form ---\n\n"
                f"From: {name} <{email}>\n"
                f"To: {audience_label}\n"
                f"Event: {event if event else 'N/A'}\n\n"
                f"Message:\n{message}\n\n"
                f"---\nSent on {now().strftime('%Y-%m-%d %H:%M')} from {request.get_host()}"
            )

            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(
                settings, "EMAIL_HOST_USER", None
            )

            msg = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=from_email,
                to=team_emails,
            )

            # Reply-To (do it one way only)
            if email:
                msg.reply_to = [email]

            # -------------------- Send with real debug + correct UX --------------------
            try:
                logger.info(
                    "CONTACT: sending email from=%s to=%s subject=%s",
                    msg.from_email,
                    team_emails,
                    email_subject,
                )

                sent = msg.send(fail_silently=False)

                # Django can return 0 without raising -> treat as failure
                if sent <= 0:
                    logger.error("CONTACT: msg.send returned %s (no recipients accepted).", sent)
                    messages.error(request, "❌ Email could not be sent. Please try again later.")
                    return redirect("contact:contact")

                messages.success(request, "✅ Thanks! Your message was sent.")
                return redirect("contact:contact_success")

            except smtplib.SMTPRecipientsRefused as e:
                logger.exception("CONTACT: SMTPRecipientsRefused: %s", e)
                messages.error(request, "❌ Could not deliver the email (invalid recipient address).")
                return redirect("contact:contact")

            except smtplib.SMTPResponseException as e:
                code = int(getattr(e, "smtp_code", 0) or 0)
                logger.exception("CONTACT: SMTPResponseException code=%s msg=%s", code, getattr(e, "smtp_error", b""))
                if code in TEMP_SMTP_CODES:
                    messages.warning(
                        request,
                        "⏳ Email delivery was deferred by the mail server. Please try again in a few minutes."
                    )
                else:
                    messages.error(request, "❌ Email delivery failed. Please try again later.")
                return redirect("contact:contact")

            except smtplib.SMTPAuthenticationError as e:
                logger.exception("CONTACT: SMTPAuthenticationError: %s", e)
                messages.error(
                    request,
                    "❌ Email server authentication failed. Please verify EMAIL_HOST_USER and the Gmail App Password."
                )
                return redirect("contact:contact")

            except smtplib.SMTPException as e:
                logger.exception("CONTACT: SMTPException: %s", e)
                messages.error(request, "❌ Email delivery failed. Please try again later.")
                return redirect("contact:contact")

            except Exception as e:
                logger.exception("CONTACT: Unexpected email send error: %s", e)
                messages.error(request, "❌ Unexpected error while sending your message. Please try again.")
                return redirect("contact:contact")

        # invalid form -> show message
        messages.error(request, "❌ Please fix the highlighted fields below.")

    else:
        form = ContactForm()
        form.fields["event"].queryset = upcoming_events_qs

    return render(
        request,
        "contact/contact_form.html",
        {
            "form": form,
            "countries": sorted({e["country"] for e in upcoming_events if e["country"]}),
            "upcoming_events_json": upcoming_events_json,
        },
    )
