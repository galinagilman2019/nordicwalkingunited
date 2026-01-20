


from django.db import models
from core.models.user import User
class Manual(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    available_for_roles = models.ManyToManyField(User, related_name='manuals')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
