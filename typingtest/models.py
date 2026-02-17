from django.conf import settings
from django.db import models

class Work(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=32, default="ru")
    source = models.CharField(max_length=255, blank=True)  # e.g. "Public domain", "Gutenberg", "Wikisource"

    def __str__(self):
        a = f" — {self.author}" if self.author else ""
        return f"{self.title}{a}"

class Passage(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="passages")
    text = models.TextField()
    chars_count = models.PositiveIntegerField(default=0)
    words_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        t = (self.text or "").strip()
        self.chars_count = len(t)
        self.words_count = len([w for w in t.split() if w.strip()])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.work} ({self.words_count} words)"

class TypingResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    passage = models.ForeignKey(Passage, on_delete=models.SET_NULL, null=True)

    duration_ms = models.PositiveIntegerField()
    typed_chars = models.PositiveIntegerField()
    correct_chars = models.PositiveIntegerField()
    errors = models.PositiveIntegerField()

    wpm = models.FloatField()
    cpm = models.FloatField()
    accuracy = models.FloatField()  # 0..100

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.user.username if self.user_id else "Anon"
        return f"{who} — {self.wpm:.1f} WPM, {self.accuracy:.1f}%"
