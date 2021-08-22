from django.conf.urls import include, url
from rest_framework import routers

from node.views.node import NodeViewSet, NodePrintJobViewSet

router = routers.SimpleRouter()
router.register('node', NodeViewSet)
router.register('print-job', NodePrintJobViewSet)

urlpatterns = [
    url(r'api/', include(router.urls)),
]
