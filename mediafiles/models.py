from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from jsonfield import JSONField
metadata = JSONField(null=True, blank=True)



FILE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        # ... add more if needed
    ]

class MediaFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='mediafiles/')
    filetype = models.CharField(max_length=10, choices=FILE_TYPES, default='image')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    tags = TaggableManager(blank=True)


