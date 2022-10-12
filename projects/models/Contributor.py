from django.conf import settings
from django.db import models


class Contributor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE)
    permission = models.CharField(max_length=100, blank=True, choices=[
        ("author", "author"),
        ("editor", "editor"),
    ])
    role = models.CharField(max_length=100, blank=True)
