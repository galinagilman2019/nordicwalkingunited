from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, help_text="URL slug (auto-filled from title if empty)")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="blog_posts"
    )
    #body = models.TextField()
    body = CKEditor5Field('Text', config_name='extends',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Publishing controls
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # auto slug
        if not self.slug:
            base = slugify(self.title)[:200]
            slug = base
            i = 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug

        # auto published_at
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        if not self.is_published:
            # allow drafts to clear published_at if toggled off
            self.published_at = None

        super().save(*args, **kwargs)
# blog/models.py


class Comment(models.Model):
    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    body = models.TextField()

    images = CKEditor5Field(
        "Images",
        config_name="comment",
        blank=True,
        null=True,
    )

    # NEW: emoji reaction counters
    reactions_leaf = models.PositiveIntegerField(default=0)     # 🌿
    reactions_heart = models.PositiveIntegerField(default=0)    # ❤️
    reactions_smile = models.PositiveIntegerField(default=0)    # 😊

    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comment_replies",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"


"""
class Comment(models.Model):
    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    body = models.TextField()

    # CKEditor field – uses CKEDITOR_5_CONFIGS["comment"]
    images = CKEditor5Field(
        "Images",
        config_name="comment",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comment_replies",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"




class Comment(models.Model):
    post = models.ForeignKey("blog.Post", on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)  # <-- made optional
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    # reply fields (from earlier)
    reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comment_replies",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
"""