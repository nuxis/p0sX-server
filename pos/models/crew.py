from django.contrib.auth.models import User

from django.db import models

from .stock import Order


class Crew(models.Model):
    card = models.CharField(max_length=255, unique=True,
                            primary_key=True, db_index=True)
    credit = models.IntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)
    crew = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.EmailField()

    @property
    def used(self):
        orders = Order.objects.filter(crew_id=self.card)
        return sum([order.sum for order in orders])

    @property
    def left(self):
        return self.credit - self.used

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class CrewSession(models.Model):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField()
    crew = models.ForeignKey(Crew)
    user = models.ForeignKey(User)
