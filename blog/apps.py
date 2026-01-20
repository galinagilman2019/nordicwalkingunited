# blog/apps.py
import os
from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "Blog"

    # 👇 This is what Django is asking for
    path = os.path.dirname(os.path.abspath(__file__))
