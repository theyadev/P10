from django.conf import settings
from django.db import models

from rest_framework import serializers

from .Contributor import ContributorSerializer


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=8192, blank=True)
    type = models.CharField(max_length=100, blank=True)
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Contributor", related_name="projects")


class ProjectSerializer(serializers.ModelSerializer):
    contributors = ContributorSerializer(
        read_only=True, many=True, source='contributor_set')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'contributors']
