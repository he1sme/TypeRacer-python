from django.urls import re_path
from .consumers import RaceConsumer

websocket_urlpatterns = [
    re_path(r"^ws/race/(?P<code>[A-Za-z0-9]+)/$", RaceConsumer.as_asgi()),
]
