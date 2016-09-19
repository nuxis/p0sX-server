from django.db import models


class User(models.Model):
    card = models.CharField(max_length=255, unique=True, primary_key=True)
    credit = models.IntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)
    crew = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
