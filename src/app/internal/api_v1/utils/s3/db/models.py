from django.db import models

class RemoteImage(models.Model):
  uploaded_at = models.DateTimeField(auto_now_add=True)
  remote_url = models.URLField(max_length=200)
  content = models.ImageField(null=False)