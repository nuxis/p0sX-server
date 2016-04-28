from django.db import models


class Log(models.Model):
    when = models.DateTimeField(auto_now=True, auto_now_add=True, blank=False)
    what = models.CharField(max_length=255)
    who = models.ForeignKey(User)

    def __str__(self):
        return '{0} gjorde {1} følgende: {2}'.format(when, who, what)
