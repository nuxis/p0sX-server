from django.db import models


class NodePrintJobQuerySet(models.QuerySet):

    def created(self):
        return self.filter(status=self.model.STATUS.created)

    def queued(self):
        return self.filter(status=self.model.STATUS.queued)
