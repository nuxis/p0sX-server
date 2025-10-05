from django.contrib.auth.models import User as DjangoUser
from django.db import models

from pos.service.sumup import delete_sumup_reader
from pos.models.stock import PAYMENT_STATE, PaymentState
from pos.models.user import User

class SumupReader(models.Model):
    name = models.CharField(max_length=255)
    reader_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(DjangoUser, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        delete_sumup_reader(self.reader_id)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'SumUp Card Reader'
        verbose_name_plural = 'SumUp Card Readers'


class SumupTransaction(models.Model):
    user = models.ForeignKey(User, related_name='transaction_user', on_delete=models.CASCADE)
    authenticated_user = models.ForeignKey(User, related_name='transaction_authorized_user', on_delete=models.CASCADE)
    amount = models.IntegerField()
    payment_state = models.SmallIntegerField(default=PaymentState.Pending, choices=PAYMENT_STATE)
    payment_reference = models.CharField(max_length=256, blank=True, null=True)
    used = models.BooleanField(default=False)
