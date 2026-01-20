from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import logging
logger = logging.getLogger('djangogirls')
today = date.today()


def validate_approximatedate(e_date):
    logger.debug(f"Validate:e_date {e_date}")
    if e_date.month == 0:
        raise ValidationError(_("Event date can't be a year only. " "Please, provide at least a month and a year."))


def validate_event_date(e_date):

    if date(e_date.year, e_date.month, e_date.day) - today < timedelta(days=1):
        raise ValidationError(
            _("Your event date is too close. " "Event date should be at least 1 day from now.")
        )


def validate_future_date(e_date):
    logger.debug(f"Validate_future_date: {date(e_date.year, e_date.month, e_date.day)}")
    if date(e_date.year, e_date.month, e_date.day) - today < timedelta(days=0):
        raise ValidationError(_("Event date should be in the future"))


