"""
Tests for utils.
"""
from django.test import TestCase

from core.utils import WersowChannel


class TestWersowChannel(TestCase):
    """Tests for WersowChannel."""

    def setUp(self):
        self.wersow_channel = WersowChannel()

    def test_channel_initializes_successful(self):
        """Test Wersow's channel initializes successful."""
        pytube_channel = self.wersow_channel.channel

        self.assertEqual(pytube_channel.channel_name, "WERSOW")

    def test_video_urls_not_empty(self):
        """Test that video_urls list is not empty."""
        video_urls = self.wersow_channel.get_video_urls()

        is_empty = len(video_urls) == 0
        self.assertFalse(is_empty)

    def test_get_latest_video_url(self):
        """Test get_latest_video_url returns url."""
        url = self.wersow_channel.get_latest_video_url()

        self.assertIn("https://www.youtube.com", url)
