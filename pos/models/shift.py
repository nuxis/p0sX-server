from django.contrib.auth.models import User
from django.db import models

from pos.models.crew import Crew


class Shift(models.Model):
    start = models.DateTimeField(auto_now_add=True, blank=False)
    end = models.DateTimeField(blank=True, null=True)
    authenticated_user = models.ForeignKey(User)
    crew = models.ForeignKey(Crew)

    def __str__(self):
        return 'Kasse: ' + str(self.authenticated_user) + ' som startet ' + self.start.strftime('%Y-%m-%d %H:%M:%S')
