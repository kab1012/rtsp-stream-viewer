import uuid
from django.db import models

# Create your models here.

class StreamSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rtsp_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Stream {self.id} - {self.rtsp_url}"
