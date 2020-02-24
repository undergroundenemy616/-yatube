from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("404/", views.page_not_found, name="page_not_found"),
    path("500/", views.server_error, name="server_error"),
    path("new/", views.new_post, name="new_post"),
    path("<username>/", views.profile, name="profile"),
    # Просмотр записи
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path("<username>/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("group/<slug:slug>", views.group_posts),
]
