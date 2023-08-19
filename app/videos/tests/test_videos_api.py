"""
Tests for videos API.
"""
import datetime

from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Video, UserVideoRelation
from videos.serializers import VideoSerializer, ReadCollectedVideoSerializer


TODAYS_URL = reverse("videos:todays")
MY_VIDEOS_URL = reverse("videos:my-videos")
COLLECT_VIDEO_URL = reverse("videos:collect-video")

VIDEO_EXAMPLE = {
    "title": "POZNALIŚMY PŁEĆ NASZEGO DZIECKA!",
    "url": "https://www.youtube.com/watch?v=Obbi-NZu7IA",
    "thumbnail_url": "https://i.ytimg.com/vi/Obbi-NZu7IA/hqdefault.jpg?sqp=-oaymwEcCPYBEIoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCSMFXYUVNWXxmDADt2R8T8JLo6iQ",  # noqa: E501
    "publish_date": datetime.date(2023, 3, 7),
}


def create_video(**params):
    """Helper function to create a video."""
    video = Video.objects.create(
        title=params.pop("title", VIDEO_EXAMPLE["title"]),
        url=params.pop("url", VIDEO_EXAMPLE["url"]),
        thumbnail_url=params.pop("thumbnail_url", VIDEO_EXAMPLE["thumbnail_url"]),
        publish_date=params.pop("publish_date", VIDEO_EXAMPLE["publish_date"]),
        **params
    )
    return video


class PublicVideosAPITests(APITestCase):
    """Test unauthenticated API requests."""

    def test_todays_video_works(self):
        """Test today's video endpoint."""
        todays_video = create_video(todays=True)

        res = self.client.get(TODAYS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = VideoSerializer(todays_video)
        self.assertEqual(res.data, serializer.data)

    def test_todays_video_error_when_no_todays_video(self):
        """Test today's video endpoint sets a random video as today's
        when there are no today's videos in database."""
        video = create_video(todays=False)

        res = self.client.get(TODAYS_URL)

        video.refresh_from_db()
        self.assertTrue(video.todays)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = VideoSerializer(video)
        self.assertEqual(res.data, serializer.data)

    def test_todays_video_error_when_no_videos(self):
        """Test today's video endpoint responses with an error
        when there are no videos at all in database."""
        res = self.client.get(TODAYS_URL)

        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_todays_video_when_multiple_todays_videos(self):
        """Test today's video endpoint responses with the latest today's video
        when there are multiple today's videos in database."""
        create_video(publish_date=datetime.date(2023, 2, 14), todays=True)
        latest_video = create_video(
            publish_date=datetime.date(2023, 2, 16), todays=True
        )

        res = self.client.get(TODAYS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        latest_video.refresh_from_db()
        serializer = VideoSerializer(latest_video)
        self.assertEqual(res.data, serializer.data)

    def test_my_videos_requires_authentication(self):
        """Test my videos endpoint requires authentication."""
        res = self.client.get(MY_VIDEOS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_collect_video_requires_authentication(self):
        """Test collect video endpoint requires authentication."""
        video = create_video()
        payload = {"video_id": video.id}

        res = self.client.post(COLLECT_VIDEO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVideosAPITests(APITestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create(
            email="test@example.com", password="testpass123", username="testuser"
        )
        self.client.force_authenticate(self.user)

    def test_my_videos_lists_videos(self):
        """Test my-videos endpoint returns a list of videos collected by user."""
        user_video_relations = [
            UserVideoRelation.objects.create(user=self.user, video=create_video())
            for _ in range(3)
        ]

        res = self.client.get(MY_VIDEOS_URL)

        self.assertEqual(res.status_code, 200)
        for user_video in user_video_relations:
            serializer = ReadCollectedVideoSerializer(user_video)
            self.assertIn(serializer.data, res.data)
            collected = user_video.collected
            self.assertEqual(str(collected), serializer.data["collected"])
            video_data = VideoSerializer(user_video.video).data
            self.assertEqual(video_data, serializer.data["video"])

    def test_my_videos_limited_to_authenticated_user(self):
        """Test my-videos list is limited to authenticated user's videos."""
        user_video = UserVideoRelation.objects.create(
            user=self.user, video=create_video()
        )
        other_user = get_user_model().objects.create(
            email="other@example.com", password="testpass123", username="otheruser"
        )
        other_user_video = UserVideoRelation.objects.create(
            user=other_user, video=create_video()
        )

        res = self.client.get(MY_VIDEOS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_video_serializer = ReadCollectedVideoSerializer(user_video)
        self.assertIn(user_video_serializer.data, res.data)
        other_user_video_serializer = ReadCollectedVideoSerializer(other_user_video)
        self.assertNotIn(other_user_video_serializer.data, res.data)

    def test_my_videos_sorted_by_collected_date(self):
        """Test my_videos list is sorted by collected date."""
        UserVideoRelation.objects.create(
            user=self.user, video=create_video(), collected=datetime.date(2023, 2, 14)
        )
        UserVideoRelation.objects.create(
            user=self.user, video=create_video(), collected=datetime.date(2023, 2, 16)
        )
        UserVideoRelation.objects.create(
            user=self.user, video=create_video(), collected=datetime.date(2023, 2, 18)
        )

        res = self.client.get(MY_VIDEOS_URL)

        user_video_relations = UserVideoRelation.objects.all().order_by("-collected")
        serializer = ReadCollectedVideoSerializer(user_video_relations, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_collect_video_user_can_collect_video(self):
        """Test user can collect video by posting video_id."""
        video = create_video()

        payload = {"video_id": video.id}
        res = self.client.post(COLLECT_VIDEO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        collected_successfully = UserVideoRelation.objects.filter(
            user=self.user, video=video
        ).exists()
        self.assertTrue(collected_successfully)

    def test_collect_not_existing_video_error(self):
        """Test that user can't collect a video that doesn't exist."""
        payload = {"video_id": -1}
        res = self.client.post(COLLECT_VIDEO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(UserVideoRelation.objects.all().exists())
        self.assertFalse(Video.objects.all().exists())

    def test_collect_video_user_cant_set_collected_date(self):
        """Test that user can't set collected date when collecting video."""
        video = create_video()

        payload = {"collected": datetime.date(2022, 5, 22), "video_id": video.id}
        self.client.post(COLLECT_VIDEO_URL, payload)

        user_video = UserVideoRelation.objects.get(user=self.user, video=video)
        self.assertEqual(user_video.collected, datetime.date.today())
