from django.contrib.auth.models import AbstractUser # type: ignore
from django.db import models  # type: ignore


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='book_covers/', null=True, blank=True)

    def __str__(self):
        return self.title
