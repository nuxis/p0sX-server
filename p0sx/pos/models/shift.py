from django.contrib.auth.models import User as DjangoUser
from django.db import models

from pos.models.user import User


class Shift(models.Model):
    start = models.DateTimeField(auto_now_add=True, blank=False)
    end = models.DateTimeField(blank=True, null=True)
    authenticated_user = models.ForeignKey(DjangoUser)
    user = models.ForeignKey(User)

    def __str__(self):
        return 'Kasse: ' + str(self.authenticated_user) + ' som startet ' + self.start.strftime('%Y-%m-%d %H:%M:%S')
