from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from race.models import RaceRoom


def _state_key(code: str) -> str:
    return f"race_state:{code}"


class Command(BaseCommand):
    help = "Delete stale race rooms that have no active players (no cached state) and are older than a threshold."

    def add_arguments(self, parser):
        parser.add_argument("--hours", type=int, default=6, help="Delete rooms older than N hours (default 6) if no cached state exists.")

    def handle(self, *args, **options):
        hours = options["hours"]
        cutoff = timezone.now() - timedelta(hours=hours)
        qs = RaceRoom.objects.filter(created_at__lt=cutoff)

        deleted = 0
        for room in qs:
            if cache.get(_state_key(room.code)) is None:
                room.delete()
                deleted += 1

        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} stale rooms."))
