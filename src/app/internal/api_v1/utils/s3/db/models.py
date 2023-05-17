from django.db import models

class RemoteImage(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    content = models.ImageField(null=False)