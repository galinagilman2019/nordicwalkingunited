
# blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.post_list, name="post_list"),           # blog:post_list
    path("<slug:slug>/", views.post_detail, name="post_detail"),
    path(
        "blog/comment/<int:pk>/react/",
        views.comment_react,
        name="comment_react",
    ),
]
