from django.contrib import admin
from .models import RaceRoom, RaceResult


@admin.register(RaceRoom)
class RaceRoomAdmin(admin.ModelAdmin):
    list_display = ("code", "created_by", "duration_sec", "created_at")
    search_fields = ("code",)


@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "wpm", "accuracy", "errors", "created_at")
    list_select_related = ("room", "user")
