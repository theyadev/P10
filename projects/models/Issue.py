from django.conf import settings
from django.db import models


class Issue(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=8192, blank=True)
    tag = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=100, blank=True)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="issues")
    status = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issues")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="assigned_issues")
    created_at = models.DateTimeField(auto_now_add=True)
