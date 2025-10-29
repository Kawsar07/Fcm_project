from django.db import models
from django.contrib.auth.models import User  # Or your custom User model

class FCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    device_id = models.CharField(max_length=100, blank=True)  # Optional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'device_id')  # One token per device per user

    def __str__(self):
        return f"{self.user.username} - {self.token[:50]}..."