from django.contrib.auth.models import User as DjangoUser

from django.db import models

from .stock import Order


class CreditUpdate(models.Model):
    user = models.ForeignKey('User', related_name='user')
    updated_by_user = models.ForeignKey('User', related_name='updated_by_user')
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user, updated_by_user, amount):
        update = cls(user=user, updated_by_user=updated_by_user, amount=amount)

        return update

    def __str__(self):
        return f'{self.updated_by_user} added {self.amount} kr to {self.user}'


class User(models.Model):
    card = models.CharField(max_length=255, unique=True, blank=False)
    credit = models.IntegerField(default=0)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=12, blank=True)
    crew = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    is_cashier = models.BooleanField(default=False)
    is_crew = models.BooleanField(default=False)

    @property
    def used(self):
        orders = Order.objects.filter(user_id=self.id)
        return sum([order.sum for order in orders])

    @property
    def left(self):
        return self.credit - self.used

    @classmethod
    def create(cls, card, credit, first_name, last_name, phone, email):
        user = cls(card=card,
                   credit=credit,
                   first_name=first_name,
                   last_name=last_name,
                   phone=phone,
                   email=email)

        return user

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    class Meta:
        permissions = (
            ("update_credit", "Can update the credit limit on a user"),
        )


class UserSession(models.Model):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField()
    user = models.ForeignKey(User)
    django_user = models.ForeignKey(DjangoUser, blank=True)
