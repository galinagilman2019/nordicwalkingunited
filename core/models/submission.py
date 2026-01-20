import uuid
from django.db import models
from core.models import User, Event
#from django_ckeditor_5.widgets import CKEditor5Widget
from django_ckeditor_5.fields import CKEditor5Field

from django_resized import ResizedImageField
class Submission(models.Model):
    participant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="submissions"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    details = models.TextField(null=True, blank=False)
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    def can_user_edit(self, user):
        """
        Returns True if `user` is:
          - the submission author, OR
          - the event's main organizer, OR
          - in the event.team (co-organizers)
        """
        if not user.is_authenticated:
            return False

        # 1) the person who posted the comment
        if user == self.participant:
            return True

        # 2) the event's main_organizer
        if self.event.main_organizer and user == self.event.main_organizer:
            return True

        # 3) any team member (ManyToMany on Event.team)
        if self.event.team.filter(id=user.id).exists():
            return True

        return False
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    #preview = CKEditor5Field('Picture', config_name='extends',null=True, blank=True)
    #preview = CKEditor5Field('Picture', config_name='default', blank=True)
    preview = CKEditor5Field('Picture', config_name='extends',null=True, blank=True)
    imgpresent = ResizedImageField(
    size=[700, 522],
    verbose_name="Image",
    blank=True,
    null=True,
    upload_to='submissions/'
)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.event.name} --- {self.participant.email if self.participant else 'Anonymous'} --- {self.id}"

