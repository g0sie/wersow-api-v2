"""
Tests for models.
"""
import datetime

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Video
from core.utils import NoVideosException


def create_user(**params):
    """Helper function for creating users."""
    email = params.pop("email", "test@example.com")
    password = params.pop("password", "testpass123")
    username = params.pop("username", "testusername")

    return get_user_model().objects.create_user(
        email=email, password=password, username=username, **params
    )


class UserModelTests(TestCase):
    """Test User model."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        username = "testusername"
        user = create_user(email=email, password=password, username=username)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.username, username)

    def test_new_user_is_active(self):
        """Test user is active by default."""
        user = create_user()

        self.assertTrue(user.is_active)

    def test_new_user_is_not_staff(self):
        """Test user is not staff by default."""
        user = create_user()

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["TEST1@example.com", "TEST1@example.com"],
            ["test2@EXAMPLE.com", "test2@example.com"],
            ["test3@example.COM", "test3@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password="testpass123", username="testusername"
            )
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without an email raises ValueError."""
        with self.assertRaises(ValueError):
            create_user(email="")

    def test_create_user_without_password_raises_error(self):
        """Test that creating a user without a password raises ValueError."""
        with self.assertRaises(ValueError):
            create_user(password="")

    def test_create_user_without_username_raises_error(self):
        """Test that creating a user without a username raises ValueError."""
        with self.assertRaises(ValueError):
            create_user(username="")

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass123", username="admin"
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_superuser_without_username_successful(self):
        """Test creating a superuser without passing username works."""
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass123"
        )

        self.assertEqual(superuser.username, "admin")
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


VIDEO_EXAMPLE = {
    "title": "POZNALIŚMY PŁEĆ NASZEGO DZIECKA!",
    "url": "https://www.youtube.com/watch?v=Obbi-NZu7IA",
    "thumbnail_url": "https://i.ytimg.com/vi/Obbi-NZu7IA/hqdefault.jpg?sqp=-oaymwEcCPYBEIoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCSMFXYUVNWXxmDADt2R8T8JLo6iQ",  # noqa: E501
    "publish_date": datetime.date(2023, 3, 7),
    "todays": True,
}


def create_video(**params):
    """Helper function for creating a video."""
    video = Video.objects.create(
        title=params.pop("title", VIDEO_EXAMPLE["title"]),
        url=params.pop("url", VIDEO_EXAMPLE["url"]),
        thumbnail_url=params.pop("thumbnail_url", VIDEO_EXAMPLE["thumbnail_url"]),
        publish_date=params.pop("publish_date", VIDEO_EXAMPLE["publish_date"]),
        **params,
    )
    return video


class VideoTests(TestCase):
    """Test Video model."""

    def test_create_video(self):
        """Test creating a video is successful."""
        video = create_video(**VIDEO_EXAMPLE)

        self.assertEqual(str(video), VIDEO_EXAMPLE["title"])
        self.assertEqual(video.title, VIDEO_EXAMPLE["title"])
        self.assertEqual(video.url, VIDEO_EXAMPLE["url"])
        self.assertEqual(video.thumbnail_url, VIDEO_EXAMPLE["thumbnail_url"])
        self.assertEqual(video.publish_date, VIDEO_EXAMPLE["publish_date"])
        self.assertEqual(video.todays, VIDEO_EXAMPLE["todays"])

    def test_new_video_is_not_todays_by_default(self):
        """Test video is not todays by default."""
        video_data = {**VIDEO_EXAMPLE}
        video_data.pop("todays")
        video = create_video(**video_data)

        self.assertFalse(video.todays)

    def test_random_video(self):
        """Test random method works."""
        video = create_video()

        random_video = Video.objects.random()

        self.assertEqual(video, random_video)

    def test_random_video_error_when_no_videos(self):
        """Test that random method raises exception
        when there are no videos in database."""
        with self.assertRaises(NoVideosException):
            Video.objects.random()

    def test_set_random_video_as_todays(self):
        """Test set_random_video_as_todays sets random video's todays field to True."""
        video = create_video(todays=False)

        todays_video = Video.objects.set_random_video_as_todays()

        video.refresh_from_db()
        self.assertEqual(video, todays_video)
        self.assertTrue(video.todays)

    def test_set_random_video_as_todays_error_when_no_videos(self):
        """Test set_random_video_as_todays raises exception
        when there are no videos in database."""
        with self.assertRaises(NoVideosException):
            Video.objects.set_random_video_as_todays()

    def test_todays_video_works(self):
        """Test todays method returns today's video."""
        video = create_video(todays=True)

        todays_video = Video.objects.todays()

        self.assertEqual(todays_video, video)

    def test_todays_video_sets_new_todays_when_no_todays(self):
        """Test todays method sets random video as today's video
        when there are no today's videos."""
        video = create_video(todays=False)

        todays_video = Video.objects.todays()

        video.refresh_from_db()
        self.assertTrue(video.todays)
        self.assertEqual(todays_video, video)

    def test_todays_video_error_when_no_videos(self):
        """Test that todays method raises exception
        when there are no videos in database."""
        with self.assertRaises(NoVideosException):
            Video.objects.todays()

    def test_todays_video_when_multiple_todays_videos(self):
        """Test that todays method returns latest video
        when there are multiple today's videos."""
        create_video(publish_date=datetime.date(2022, 5, 22), todays=True)
        latest_todays_video = create_video(
            publish_date=datetime.date(2023, 3, 7), todays=True
        )

        todays_video = Video.objects.todays()

        self.assertEqual(todays_video, latest_todays_video)

    def test_add_video_works(self):
        """Test add_video method works."""
        video_url = VIDEO_EXAMPLE["url"]
        Video.objects.add_video(video_url=video_url)

        video_is_added = Video.objects.filter(title=VIDEO_EXAMPLE["title"]).exists()
        self.assertTrue(video_is_added)

    @patch("core.models.Video.objects.random")
    def test_change_todays_video_works(self, patched_random):
        """Test change_todays_video method changes today's video."""
        old_todays = create_video(todays=True)
        next_todays = create_video(todays=False)

        patched_random.return_value = next_todays
        Video.objects.change_todays_video()

        old_todays.refresh_from_db()
        self.assertFalse(old_todays.todays)
        next_todays.refresh_from_db()
        self.assertTrue(next_todays.todays)

    def test_change_todays_video_when_no_todays_videos(self):
        """Test change_todays_video sets new today's video
        when there is no today's video."""
        video = create_video(todays=False)

        Video.objects.change_todays_video()

        video.refresh_from_db()
        self.assertTrue(video.todays)

    def test_change_todays_video_error_when_no_videos(self):
        """Test change_todays_video raises exception
        when there are no videos in database."""
        with self.assertRaises(NoVideosException):
            Video.objects.change_todays_video()

    @patch("core.models.Video.objects.random")
    def test_change_todays_video_when_multiple_todays_videos(self, patched_random):
        """Test that change_todays_video leaves database with only one today's video
        even if there were more today's videos before."""
        create_video(todays=True)
        create_video(todays=True)
        next_todays = create_video(todays=False)

        patched_random.return_value = next_todays
        Video.objects.change_todays_video()

        self.assertTrue(next_todays.todays)
        todays_count = Video.objects.filter(todays=True).count()
        self.assertEqual(todays_count, 1)

    @patch("core.utils.WersowChannel.get_latest_video_url")
    def test_add_latest_video_works(self, patched_latest):
        """Test add_latest_video method adds latest Wersow's video to database."""
        url = VIDEO_EXAMPLE["url"]
        patched_latest.return_value = url
        Video.objects.add_latest_video()

        is_added = Video.objects.filter(url=url).exists()
        self.assertTrue(is_added)

    @patch("core.utils.WersowChannel.get_latest_video_url")
    def test_add_latest_video_when_latest_isnt_new(
        self,
        patched_latest_video_url,
    ):
        """Test add_latest_video doens't add latest Wersow's video
        if it's already in database."""
        url = VIDEO_EXAMPLE["url"]
        create_video(url=url)

        patched_latest_video_url.return_value = url
        Video.objects.add_latest_video()

        is_added = Video.objects.filter(url=url).count() > 1
        self.assertFalse(is_added)
