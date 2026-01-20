from django.contrib import admin
from django import forms
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Post, Comment
from core.models import Event
#

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Post, Comment
from core.models import Event
#

# -------------------------
# INLINE COMMENTS ON POSTS
# -------------------------
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = (
        "name",
        "email",
        "body",
        # you can add "images" here if you REALLY want it inline,
        # but CKEditor inside tabular inline is often cramped:
        # "images",
        "is_approved",
        "reply",
        "replied_at",
        "replied_by",
        "created_at",
    )
    readonly_fields = ("created_at", "replied_at", "replied_by")
    can_delete = True

    def has_change_permission(self, request, obj=None):
        """
        Inline respects same permissions: organizer can only
        edit comments on their own posts.
        """
        if request.user.is_superuser:
            return True
        # Inlines are only shown for posts the user can access via PostAdmin.get_queryset,
        # so we can just allow here.
        return True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Blog posts:
    - author set automatically to current user
    - slug & published_at hidden and auto-filled
    - only superuser / organizers can add posts
    - non-superusers only see their own posts
    """

    list_display = ("title", "author", "is_published", "published_at")
    search_fields = ("title", "author__name", "author__email")

    exclude = ("author", "slug", "published_at")

    inlines = [CommentInline]

    # custom changelist template to show blog stats
    change_list_template = "admin/blog/post_change_list.html"

    # ---------- QUERY RESTRICTION ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    # ---------- ROLE HELPERS ----------
    def _is_organizer(self, user):
        if not user.is_authenticated:
            return False
        return Event.objects.filter(
            Q(main_organizer=user) | Q(team=user)
        ).exists()

    # ---------- PERMISSIONS ----------
    def has_add_permission(self, request):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or self._is_organizer(user):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        base = super().has_change_permission(request, obj)
        if not base:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.author_id == user.id

    # ---------- AUTO-FILL FIELDS ----------
    def save_model(self, request, obj, form, change):
        # Author
        if not change or obj.author is None:
            obj.author = request.user

        # Slug: if empty, build from title
        if not obj.slug:
            base = obj.title or "post"
            obj.slug = slugify(base)[:50]

        # Published_at
        if obj.is_published and obj.published_at is None:
            obj.published_at = timezone.now()

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if "author" not in fields:
            fields.append("author")
        return fields

    # ---------- BLOG DASHBOARD STATS ON POST LIST ----------
    def changelist_view(self, request, extra_context=None):
        """
        Add blog stats (comment counts, pending comments, latest comments)
        to the Post changelist page as a 'dashboard' widget.
        """
        qs_posts = self.get_queryset(request)
        qs_comments = Comment.objects.filter(post__in=qs_posts)

        stats = {
            "total_posts": qs_posts.count(),
            "total_comments": qs_comments.count(),
            "pending_comments": qs_comments.filter(is_approved=False).count(),
            "latest_comments": qs_comments.select_related("post").order_by("-created_at")[:5],
        }

        extra_context = extra_context or {}
        extra_context["blog_stats"] = stats

        return super().changelist_view(request, extra_context=extra_context)


# -------------------------
# COMMENT ADMIN FORM (with CKEditor for images)
# -------------------------
class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
        widgets = {
            "images": CKEditor5Widget(config_name="comment"),
        }


@admin.register(Comment)

class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm

    list_display = ("post", "name", "email", "created_at", "is_approved", "short_reply")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "email", "body", "reply")

    actions = ["approve_comments"]

    fields = (
        "post",
        "name",
        "email",
        "body",
        "images",        # <- show CKEditor field here
        "is_approved",
        "reply",
        "replied_at",
        "replied_by",
        "created_at",
    )
    readonly_fields = ("created_at", "replied_at", "replied_by")

    # -------------------------
    # Utility for list_display
    # -------------------------
    @admin.display(description=_("Reply"))
    def short_reply(self, obj):
        if not obj.reply:
            return ""
        return (obj.reply[:40] + "…") if len(obj.reply) > 40 else obj.reply

    # -------------------------
    # Limit visible comments
    # -------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs

        # organizer: only comments on posts they authored
        return qs.filter(post__author=user)

    # -------------------------
    # Limit edit/approve/delete
    # -------------------------
    def has_change_permission(self, request, obj=None):
        user = request.user

        if user.is_superuser:
            return True

        if obj is not None:
            return obj.post.author_id == user.id

        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    # -------------------------
    # Save reply metadata
    # -------------------------
    #def save_model(self, request, obj, form, change):
    #    """
    #    If reply text was changed/added, set replied_by and replied_at.
    #    """
    #    from django.utils import timezone as dj_timezone

    #    if "reply" in form.changed_data and obj.reply:
    #        obj.replied_by = request.user
    #        obj.replied_at = dj_timezone.now()

    #    super().save_model(request, obj, form, change)
    #
        # -------------------------
    # Save reply metadata + email notification
    # -------------------------
    def save_model(self, request, obj, form, change):
        """
        If reply text was changed/added, set replied_by and replied_at,
        then email the commenter (if email is provided).
        """
        from django.utils import timezone as dj_timezone

        # Detect if reply changed to a non-empty value
        reply_changed = "reply" in form.changed_data and bool(obj.reply)

        if reply_changed:
            obj.replied_by = request.user
            obj.replied_at = dj_timezone.now()

        # Save first
        super().save_model(request, obj, form, change)

        # Send notification email
        if reply_changed and obj.email:
            try:
                context = {
                    "comment": obj,
                    "post": obj.post,
                    "url": request.build_absolute_uri(obj.post.get_absolute_url()),
                }
                subject = _("New reply to your comment on '%(title)s'") % {
                    "title": obj.post.title
                }
                message = render_to_string("blog/email_comment_reply.txt", context)

                send_mail(
                    subject,
                    message,
                    getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    [obj.email],
                    fail_silently=True,  # avoid breaking admin if email fails
                )
            except Exception:
                # You could log the error here if you have logging configured
                pass

    # -------------------------
    # Approve action
    # -------------------------
    @admin.action(description=_("Approve selected comments"))
    def approve_comments(self, request, queryset):
        user = request.user

        if user.is_superuser:
            queryset.update(is_approved=True)
        else:
            queryset.filter(post__author=user).update(is_approved=True)







