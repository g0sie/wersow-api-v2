"""
Videos API
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import Video, UserVideoRelation, NoVideosException
from videos.serializers import (
    VideoSerializer,
    ReadCollectedVideoSerializer,
    CollectVideoSerializer,
)


class TodaysVideo(APIView):
    """ViewSet for retrieving today's video."""

    @extend_schema(
        responses={
            200: VideoSerializer,
            503: OpenApiResponse(description="No videos in database."),
        }
    )
    def get(self, request):
        """Retrieve today's video."""
        try:
            video = Video.objects.todays()

        except NoVideosException:
            return Response(
                "There are no videos in database.",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        serializer = VideoSerializer(video)
        return Response(serializer.data)


class MyVideos(generics.ListAPIView):
    """Get a list of videos collected by authenticated user."""

    queryset = UserVideoRelation.objects.all()
    serializer_class = ReadCollectedVideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset with authenticated user."""
        user = self.request.user
        return self.queryset.filter(user=user).order_by("-collected")


class CollectVideo(generics.CreateAPIView):
    """Collect a video."""

    serializer_class = CollectVideoSerializer
    permission_classes = [IsAuthenticated]
