from django.contrib import admin

from .models import Location, Node, NodePrinter, NodePrintJob, NodeWebsite



admin.site.register(Location, admin.ModelAdmin)
admin.site.register(Node, admin.ModelAdmin)
admin.site.register(NodePrinter, admin.ModelAdmin)
admin.site.register(NodeWebsite, admin.ModelAdmin)
admin.site.register(NodePrintJob, admin.ModelAdmin)
