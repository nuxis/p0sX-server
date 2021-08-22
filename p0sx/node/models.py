from django.db import models
from django.utils.translation import ugettext as _

from model_utils import Choices

from node.managers.node import NodePrintJobQuerySet


class Location(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Node(models.Model):
    # This token comes from DRF
    token = models.ForeignKey('authtoken.Token', related_name='nodes', on_delete=models.deletion.PROTECT)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name or self.token


class NodePrinter(models.Model):
    PRINTER_TYPE = Choices(
        ('epson', _("Generic Epson printer")),
    )
    node = models.ForeignKey(Node, related_name='printers', on_delete=models.deletion.PROTECT)
    printer_type = models.CharField(max_length=64, choices=PRINTER_TYPE)

    def __str__(self):
        return f'{self.node} ({self.get_printer_type_display()})'


class NodeWebsite(models.Model):
    node = models.OneToOneField(Node, related_name='website', on_delete=models.deletion.CASCADE)
    # TODO: make some logic for generating these pages backend, and expose choices for those pages instead
    url = models.URLField()

    def __str__(self):
        return f'{self.node}: {self.url}'


class NodePrintJob(models.Model):
    STATUS = Choices(
        ('created', _("Created")),
        ('queued', _("Queued")),
        ('acked', _("Acknowledged by node")),
        ('printed', _("Printed")),
        ('discarded', _("Discarded")),
        ('aborted', _("Aborted")),
    )

    node = models.ForeignKey(Node, related_name='print_jobs', on_delete=models.deletion.PROTECT)
    # TODO: s/receipts/receipt/
    receipt = models.ForeignKey('pos.receipt', related_name='print_jobs', on_delete=models.deletion.PROTECT)
    status = models.TextField(max_length=64, choices=STATUS, default=STATUS.created)

    objects = NodePrintJobQuerySet.as_manager()

    def __str__(self):
        rec = _("receipt {id}").format(id=self.receipt_id)
        return f'{self.node}: {rec} ({self.get_status_display()})'
