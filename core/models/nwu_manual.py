from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
USER_TYPE_CHOICES = [
    ("handbook", "Handbook"),
    ("participant", "For Participants"),
    ("team", "For Team Members / Organizers"),
    ("general", "General Information"),
]
class NWU_Manual(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    audience = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="handbook")
    order = models.PositiveIntegerField(default=0)  # for ordering chapters
    table_title = models.CharField(max_length=200, blank=True)  # optional short title for TOC

    #body = CKEditor5Field(config_name="default")
    body = CKEditor5Field('Text', config_name='extends',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["audience", "order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

