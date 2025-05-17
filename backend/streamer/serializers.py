from rest_framework import serializers
from .models import StreamSession

class StreamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamSession
        fields = ['id', 'rtsp_url', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'is_active'] 