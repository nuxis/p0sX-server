import uuid
from datetime import timedelta

from django.contrib.auth.models import User as DjangoUser
from django.db import models, transaction
from django.utils import timezone

from pos.models.user import User
from pos.service import sumup as service


ACCESS_CODE_TIMEOUT = 60


class SumUpAPIKey(models.Model):
    """
    One single API key can be used for multiple terminals
    """
    client_id = models.CharField(max_length=512)
    client_secret = models.CharField(max_length=512)
    access_code_state = models.UUIDField(null=True, blank=True)

    token = models.CharField(max_length=256, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    refresh_token = models.CharField(max_length=256, null=True, blank=True)
    refresh_token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.client_id

    @property
    def token_expired(self):
        return self.token_expiry <= timezone.now()

    def refresh_current_token(self):
        service.refresh_token(self)

    def get_unhandled_transactions(self, seconds=300):
        """
        Get the latest unhandled transactions

        :param seconds: Number of seconds to cover
        :return: QuerySet(SumUpTransaction)
        """
        service.update_transactions(self, seconds=seconds)
        transactions = self.transactions.all().filter(timestamp__gte=timezone.now() - timedelta(seconds=seconds))
        return transactions.filter(handled=False)


class SumUpTerminal(models.Model):
    """
    Aa physical terminal
    """
    key = models.ForeignKey(SumUpAPIKey, related_name='terminals', on_delete=models.CASCADE)
    serial = models.CharField(max_length=32)


class SumUpTransaction(models.Model):
    def __str__(self):
        return '{} - {}kr ({}) [{}]'.format(
            self.transaction_code,
            self.amount,
            self.summary,
            'Handled' if self.handled else 'Unhandled'
        )
    key = models.ForeignKey(SumUpAPIKey, related_name='transactions', on_delete=models.CASCADE)
    handled = models.BooleanField(default=False)

    transaction_id = models.CharField(max_length=256)
    transaction_code = models.CharField(max_length=64)
    user = models.CharField(max_length=256)
    status = models.CharField(max_length=64)
    summary = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    timestamp = models.DateTimeField()

    @transaction.atomic
    def use_on_user(self, user, crew_user):
        """

        :param user: The user to add the credit to
        :param crew_user: The crew user adding the credit
        :return: True
        """
        if not self.status == 'SUCCESSFUL':
            return False
        user.credit += self.amount
        user.save()

        from pos.models.user import CreditUpdate
        cu = CreditUpdate.create(user, crew_user, self.amount)
        cu.save()
        self.handled = True
        self.save()
        return True


class SumUpCard(models.Model):

    def __str__(self):
        return '{} to {} with status {}'.format(self.amount, self.user, self.get_status_display())
    SUMUP_STATUS = [
        (0, 'CREATED'),
        (1, 'PROCESSING'),
        (2, 'SUCCESS'),
        (3, 'FAILED'),
        (4, 'COMPLETE'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    authorized_user = models.ForeignKey(DjangoUser, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.SmallIntegerField(choices=SUMUP_STATUS, default=0)
    transaction_id = models.CharField(max_length=64, null=True, blank=True)
    transaction_comment = models.CharField(max_length=256, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def update_user(self):
        if not self.status == 2:
            return False

        user = self.user
        user.credit += self.amount
        user.save()

        from pos.models.user import CreditUpdate
        cu = CreditUpdate.sumup_create(user=self.user, amount=self.amount)
        cu.save()
        self.status = 4
        self.save()
        return True


class SumUpOnline(models.Model):

    def __str__(self):
        return '{} to {} with status {}'.format(self.amount, self.user, self.get_status_display())
    SUMUP_STATUS = [
        (0, 'CREATED'),
        (1, 'PROCESSING'),
        (2, 'SUCCESS'),
        (3, 'FAILED'),
        (4, 'COMPLETE'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.SmallIntegerField(choices=SUMUP_STATUS, default=0)
    transaction_id = models.CharField(max_length=64, null=True, blank=True)
    transaction_comment = models.CharField(max_length=256, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def update_user(self):
        if not self.status == 2:
            return False

        user = self.user
        user.credit += self.amount
        user.save()

        from pos.models.user import CreditUpdate
        cu = CreditUpdate.sumup_create(user=self.user, amount=self.amount)
        cu.save()
        self.status = 4
        self.save()
        return True
