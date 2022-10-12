from django.conf import settings
from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=8192, blank=True)
    type = models.CharField(max_length=100, blank=True)
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Contributor", related_name="projects")
