"""
Urls for videos API
"""
from django.urls import path

from videos import views

app_name = "videos"
urlpatterns = [
    path("todays/", views.TodaysVideo.as_view(), name="todays"),
    path("my", views.MyVideos.as_view(), name="my-videos"),
    path("my/add", views.CollectVideo.as_view(), name="collect-video"),
]
