from datetime import datetime

from django.db import models


class EventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def public(self):
        """
        Only include events that are on the homepage.
        """
        return self.get_queryset().filter(is_on_homepage=True)

    def future(self):
        return self.public().filter(date__gte=datetime.now().strftime("%Y-%m-%d")).order_by("date")

#    def past(self):
#        return self.public().filter(date__isnull=False, date__lt=datetime.now().strftime("%Y-%m-%d")).order_by("-date")
    def past(self):
        return self.public().filter(date__isnull=False, date__lt=datetime.now().strftime("%Y-%m-%d")).order_by("-date")
    def nwg_distinct(self):
#        return self.get_queryset().filter(is_deleted=False).order_by('nwgroup').distinct('nwgroup')
#        return self.get_queryset().filter(is_deleted=False).order_by('nwgroup').distinct('nwgroup').values_list('nwgroup', flat=True)
        return self.get_queryset().filter(is_on_homepage=True) #Only for SQLITE#
#        return queryset.values_list('city', flat=True)
