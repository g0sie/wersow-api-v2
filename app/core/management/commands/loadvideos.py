"""
Command to get videos from Wersow's channel and add them to the database.
"""
from django.core.management.base import BaseCommand

from core.models import Video
from core.utils import WersowChannel


class Command(BaseCommand):
    help = "Adds Wersow's videos to the database"

    def add_arguments(self, parser):
        """Specify how many videos should be added (all by default)."""
        parser.add_argument(
            "--limit", type=int, help="Amount of videos to add", default=float("inf")
        )

    def handle(self, *args, **options):
        """Iterate over Wersow's videos and add them to the database."""

        channel = WersowChannel()
        to_add_limit = options.get("limit")
        added_count = 0

        video_urls = channel.get_video_urls()

        for video_url in video_urls:
            if added_count >= to_add_limit:
                break

            is_video_new = not Video.objects.filter(url=video_url).exists()
            if is_video_new:
                video = Video.objects.add_video(video_url)
                added_count += 1
                self.stdout.write(f"Added {video.title}...")

        self.stdout.write(self.style.SUCCESS(f"Added {added_count} new videos"))

        added_all = Video.objects.count() == len(video_urls)
        if added_all:
            self.stdout.write(
                self.style.SUCCESS("All Wersow's videos are in the database")
            )
