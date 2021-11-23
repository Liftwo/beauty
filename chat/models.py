from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    status = models.BooleanField(default=False)

