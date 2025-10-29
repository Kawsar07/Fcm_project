from django.db import models
from django.contrib.auth.models import User  

class FCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    device_id = models.CharField(max_length=100, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'device_id')  

    def __str__(self):
        return f"{self.user.username} - {self.token[:50]}..."