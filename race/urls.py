from django.urls import path
from . import views

urlpatterns = [
    path("", views.race_home, name="race_home"),
    path("<str:code>/", views.race_room, name="race_room"),
]
