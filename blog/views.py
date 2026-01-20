# blog/views.py
import os
import uuid
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post
from .forms import CommentForm
from .forms import Comment
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.db.models import F
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.contrib.auth import get_user_model


from django.views.decorators.http import require_POST


User = get_user_model()
import logging
logger = logging.getLogger(__name__)
#--------------
def _user_from_email(email: str):
    email = (email or "").strip()
    if not email:
        return None
    return User.objects.filter(email__iexact=email).first()
def _can_auto_approve_by_email(email: str, post) -> bool:
    u = _user_from_email(email)
    if not u:
        return False

    # superuser / organizer
    if _is_organizer(u):
        return True

    # post author (adjust field name if yours differs)
    if getattr(post, "author_id", None) == getattr(u, "id", None):
        return True

    return False
#--------------
def post_list(request):
    posts = Post.objects.order_by("-published_at")[:20]
    return render(request, "blog/post_list.html", {"posts": posts})

def _is_organizer(user) -> bool:
    if not user:
        return False
    if getattr(user, "is_superuser", False):
        return True
    if getattr(user, "is_staff", False):
        return True
    return user.groups.filter(name="Organizers").exists()


def _can_auto_approve_comment(user, post):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if getattr(post, "author_id", None) == user.id:
        return True

    # Organizer role via Django Group
    return user.groups.filter(name="Organizers").exists()


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)

    order = request.GET.get("order", "newest")

    comments_qs = post.comments.filter(is_approved=True)
    comments_qs = comments_qs.order_by(
        "-created_at" if order == "newest" else "created_at"
    )

    paginator = Paginator(comments_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ---------------- COMMENT SUBMISSION ----------------
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            email = form.cleaned_data.get("email")
            comment.is_approved = _can_auto_approve_by_email(email, post)

            comment.save()

            if comment.is_approved:
                messages.success(request, _("Your comment has been posted."))
            else:
                messages.success(request, _("Your comment has been submitted and is awaiting approval."))

            return redirect(f"{post.get_absolute_url()}?order={order}#comments")

        messages.error(request, _("Please correct the errors below."))
    else:
        form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "form": form,
            "page_obj": page_obj,
            "order": order,
        },
    )


    # -------- Handle new comment submission --------
"""
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            # Auto-approve if user is superuser / post author / NWU organizer
            if _can_auto_approve_comment(request.user, post):
                comment.is_approved = True
            # else: leave default (False) so it appears as "pending"

            comment.save()
            if comment.is_approved:
                messages.success(
                    request,
                    _("Your comment has been posted.")
                )
            else:
                messages.success(
                    request,
                    _("Your comment has been submitted and is awaiting approval.")
                )

            return redirect(f"{post.get_absolute_url()}?order={order}#comments")
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "form": form,
            "page_obj": page_obj,
            "order": order,
        },
    )
"""



@require_POST
def comment_react(request, pk):
    """
    Increment one of the emoji counters on an approved comment, then redirect back.
    """
    comment = get_object_or_404(Comment, pk=pk, is_approved=True)

    emoji = request.POST.get("emoji")

    if emoji == "leaf":
        Comment.objects.filter(pk=comment.pk).update(reactions_leaf=F("reactions_leaf") + 1)
    elif emoji == "heart":
        Comment.objects.filter(pk=comment.pk).update(reactions_heart=F("reactions_heart") + 1)
    elif emoji == "smile":
        Comment.objects.filter(pk=comment.pk).update(reactions_smile=F("reactions_smile") + 1)

    # Go back to the same page + jump to this comment
    #back = request.META.get("HTTP_REFERER") or comment.post.get_absolute_url()
    #return redirect(f"{back}#comment-{comment.pk}")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@csrf_exempt
def comment_image_upload(request):
    """
    Public CKEditor image upload endpoint for comments.

    ⚠️ Anyone can hit this URL.  We still do some basic checks:
    - POST only
    - 'upload' file must exist
    - simple size limit (5 MB)
    """
    if request.method != "POST" or "upload" not in request.FILES:
        return JsonResponse({"error": "Invalid request"}, status=400)

    upload = request.FILES["upload"]

    # Optional: simple size limit (5 MB)
    max_size = 5 * 1024 * 1024
    if upload.size > max_size:
        return JsonResponse({"error": "File too large"}, status=400)

    # Optional: restrict extensions a bit
    allowed_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(upload.name)[1].lower()
    if ext not in allowed_exts:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    # Save to MEDIA_ROOT/comment_images/...
    filename = f"comment_images/{uuid.uuid4().hex}{ext}"
    saved_name = default_storage.save(filename, ContentFile(upload.read()))
    url = default_storage.url(saved_name)

    # django_ckeditor_5 expects a JSON with "url"
    return JsonResponse({"url": url})


