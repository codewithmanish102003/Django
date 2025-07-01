from django.db import models


# Create your models here.
class Services(models.Model):
    SERVICES_TYPE_CHOICE = [
        ("UI", "FRONTEND"),
        ("LO", "BACKEND")
    ]
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='website/services') #pillow
    description=models.TextField(default="")
    type = models.CharField(max_length=8, choices=SERVICES_TYPE_CHOICE)
