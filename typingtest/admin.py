from django.contrib import admin
from .models import Work, Passage, TypingResult

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "language", "source")
    search_fields = ("title", "author")

@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ("work", "words_count", "chars_count", "created_at")
    search_fields = ("work__title", "work__author", "text")
    list_filter = ("work__language",)

@admin.register(TypingResult)
class TypingResultAdmin(admin.ModelAdmin):
    list_display = ("user", "wpm", "cpm", "accuracy", "errors", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)
