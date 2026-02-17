from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('typingtest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaceRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=8, unique=True)),
                ('chunk_text', models.TextField()),
                ('chunk_start', models.IntegerField(default=0)),
                ('duration_sec', models.IntegerField(default=60)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_races', to=settings.AUTH_USER_MODEL)),
                ('passage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_rooms', to='typingtest.passage')),
            ],
        ),
        migrations.CreateModel(
            name='RaceResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration_ms', models.IntegerField()),
                ('typed_chars', models.IntegerField()),
                ('correct_chars', models.IntegerField()),
                ('errors', models.IntegerField()),
                ('wpm', models.FloatField()),
                ('cpm', models.FloatField()),
                ('accuracy', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='race.raceroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_results', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['created_at'], name='race_raceres_created_2a4a23_idx')],
            },
        ),
    ]
