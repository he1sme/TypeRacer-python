from django.conf import settings
from django.db import models


class RaceRoom(models.Model):
    code = models.CharField(max_length=8, unique=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_races"
    )
    passage = models.ForeignKey("typingtest.Passage", on_delete=models.CASCADE, related_name="race_rooms")
    chunk_text = models.TextField()
    chunk_start = models.IntegerField(default=0)
    duration_sec = models.IntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.code}"


class RaceResult(models.Model):
    room = models.ForeignKey(RaceRoom, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="race_results")

    duration_ms = models.IntegerField()
    typed_chars = models.IntegerField()
    correct_chars = models.IntegerField()
    errors = models.IntegerField()
    wpm = models.FloatField()
    cpm = models.FloatField()
    accuracy = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["created_at"])]
