from pos.models.simplelog import Log
from pos.serializers.simplelog import LogSerializer
from rest_framework import viewsets


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
