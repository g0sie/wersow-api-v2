"""
Command to add the latest Wersow's video to the database
but only if the video is not in the database already.
"""
from django.core.management.base import BaseCommand

from core.models import Video


class Command(BaseCommand):
    help = """Add the latest Wersow's video to the database
              but only if the video is not in the database already"""

    def handle(self, *args, **options):
        latest_video = Video.objects.add_latest_video()

        if latest_video:
            self.stdout.write(self.style.SUCCESS(f"Added: {latest_video}"))

        else:
            self.stdout.write(
                self.style.SUCCESS("Latest video was already in database")
            )
