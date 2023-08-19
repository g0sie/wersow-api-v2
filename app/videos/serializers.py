"""
Serializers for videos API
"""
from rest_framework import serializers

from core.models import Video, UserVideoRelation


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model."""

    class Meta:
        model = Video
        fields = "__all__"


class CollectVideoSerializer(serializers.ModelSerializer):
    """Serializer for collecting videos."""

    video_id = serializers.IntegerField()

    class Meta:
        model = UserVideoRelation
        fields = ["video_id", "collected"]
        read_only_fields = ["collected"]

    def validate_video_id(self, video_id):
        """Check if video with given id exists."""
        if Video.objects.filter(id=video_id).exists():
            return video_id
        raise serializers.ValidationError(f"Video with id {video_id} doesn't exists.")

    def create(self, validated_data):
        """Add video to authenticated user's videos."""
        request = self.context["request"]
        user = request.user
        video_id = validated_data["video_id"]
        video = Video.objects.get(id=video_id)
        return UserVideoRelation.objects.create(user=user, video=video)


class ReadCollectedVideoSerializer(serializers.ModelSerializer):
    """Serializer for reading collected videos."""

    video = VideoSerializer()

    class Meta:
        model = UserVideoRelation
        fields = ["collected", "video"]
