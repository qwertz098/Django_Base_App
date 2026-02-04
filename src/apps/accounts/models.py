from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for the project."""

    email = models.EmailField("email address", unique=True)

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username
