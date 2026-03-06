


from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = CountryField(blank_label=True)

    def __str__(self):
        return self.user.username
