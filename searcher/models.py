from django.db import models
from django.contrib.auth.models import  AbstractUser
from django.utils import timezone

# Create your models here.


class CustomUser(AbstractUser):

    mal_account = models.URLField()
    users_manga = models.CharField(max_length=140, blank=True)
    user_anime = models.CharField(max_length=140, blank=True)
    manga_translator = models.CharField(max_length=140, blank=True)
    anime_translator = models.CharField(max_length=140, blank=True)
    last_check = models.DateTimeField(default=None, null=True)

    REQUIRED_FIELDS = ['mal_account']

    def mark_cheked(self, commit=True):
        self.last_check = timezone.now()
        if commit:
            self.save()
