from django.conf import settings
from django.db import models

from rest_framework import serializers


class Comment(models.Model):
    description = models.CharField(max_length=8192, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    issue = models.ForeignKey(
        "Issue", on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description', 'author', 'issue', 'created_at']
