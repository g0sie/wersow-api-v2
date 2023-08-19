"""
Command to change today's video.
"""
from django.core.management.base import BaseCommand

from core.models import Video


class Command(BaseCommand):
    help = "Changes today's video to another random video"

    def handle(self, *args, **options):
        new_todays = Video.objects.change_todays_video()

        self.stdout.write(self.style.SUCCESS(f"Now today's video is: {new_todays}"))
