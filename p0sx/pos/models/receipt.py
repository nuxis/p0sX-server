from django.db import models
from django.utils.translation import ugettext as _


class Receipt(models.Model):
    created = models.DateTimeField(auto_created=True)
    content = models.TextField()

    def __str__(self):
        return _("Receipt {id}").format(id=self.pk)
