from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import StreamSession
from .serializers import StreamSessionSerializer

# Create your views here.

class StreamSessionViewSet(viewsets.ModelViewSet):
    queryset = StreamSession.objects.all()
    serializer_class = StreamSessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        stream = self.get_object()
        stream.is_active = False
        stream.save()
        return Response({'status': 'stream stopped'})
