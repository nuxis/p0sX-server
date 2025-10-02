from django.contrib.auth.models import User as DjangoUser
from django.db import models


class SumupReader(models.Model):
    name = models.CharField(max_length=255)
    reader_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(DjangoUser, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'SumUp Card Reader'
        verbose_name_plural = 'SumUp Card Readers'
