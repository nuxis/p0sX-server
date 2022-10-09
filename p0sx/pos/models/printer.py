from django.contrib.auth.models import User as DjangoUser
from django.db import models


class Printer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    port = models.IntegerField(default=9100)
    user = models.ForeignKey(DjangoUser, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Printers'
