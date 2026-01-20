from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UpcomingEventsFilter(admin.SimpleListFilter):
    title = _(" upcoming / past")
    parameter_name = "when"

    def lookups(self, request, model_admin):
        return (
            ("upcoming", _("Upcoming events")),
            ("past", _("Past events")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        # Prefer DB-side filtering if you have a datetime field for the event start.
        # Adjust these field names to YOUR model if needed:
        # Common options: "starts_at", "start_datetime", "datetime", etc.
        #
        # If you don't have a single datetime field, we fall back to "date".
        now = timezone.localtime(timezone.now()).date()

        # ---- Option A: You have a DateField called `date` (you do) ----
        if value == "upcoming":
            return queryset.filter(date__gte=now)
        if value == "past":
            return queryset.filter(date__lt=now)

        return queryset
