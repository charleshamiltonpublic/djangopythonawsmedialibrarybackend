from rest_framework import serializers
from .models import MediaFile
from taggit.serializers import (TagListSerializerField,
                                           TaggitSerializer)

class MediaFileSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = MediaFile
        fields = '__all__'
