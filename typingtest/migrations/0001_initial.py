from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Work",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(blank=True, max_length=255)),
                ("language", models.CharField(default="ru", max_length=32)),
                ("source", models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Passage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                ("chars_count", models.PositiveIntegerField(default=0)),
                ("words_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("work", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="passages", to="typingtest.work")),
            ],
        ),
        migrations.CreateModel(
            name="TypingResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("duration_ms", models.PositiveIntegerField()),
                ("typed_chars", models.PositiveIntegerField()),
                ("correct_chars", models.PositiveIntegerField()),
                ("errors", models.PositiveIntegerField()),
                ("wpm", models.FloatField()),
                ("cpm", models.FloatField()),
                ("accuracy", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("passage", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="typingtest.passage")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
