from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from node.models import Node, NodePrintJob
from node.serializers.node import NodeSerializer, NodePrintJobSerializer


class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    authentication_classes = [TokenAuthentication]

    @action(detail=True)
    def get_available_print_jobs(self, request, pk):
        node = get_object_or_404(self.queryset, pk=pk)
        if node.token != self.request.auth:
            raise PermissionDenied
        jobs = node.print_jobs.created()
        serializer = NodePrintJobSerializer(jobs, many=True)
        return Response(serializer.data)


class NodePrintJobViewSet(viewsets.ModelViewSet):
    queryset = NodePrintJob.objects.all()
    serializer_class = NodePrintJobSerializer
    authentication_classes = [TokenAuthentication]

    def _get_job(self, **kwargs):
        job = get_object_or_404(self.queryset, **kwargs)
        if job.node.token != self.request.auth:
            raise PermissionDenied
        return job

    def retrieve(self, request, *args, **kwargs):
        job = self._get_job(pk=kwargs.get('pk'))
        serializer = NodePrintJobSerializer(job)
        return Response(serializer.data)

    def _update_status(self, pk, status):
        job = self._get_job(pk=pk)
        if status not in job.STATUS:
            raise ParseError
        job.status = status
        job.save()
        return Response('OK')

    @action(detail=True, methods=['post'])
    def set_queued(self, *args, **kwargs):
        return self._update_status(kwargs.get('pk'), NodePrintJob.STATUS.queued)

    @action(detail=True, methods=['post'])
    def set_printed(self, *args, **kwargs):
        return self._update_status(kwargs.get('pk'), NodePrintJob.STATUS.printed)
