
from pos.models.shift import Shift

from pos.serializers.shift import NewShiftSerializer, ShiftSerializer

from rest_framework import viewsets
from rest_framework.response import Response


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer


class CurrentShiftViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShiftSerializer

    def get_queryset(self):
        shifts = Shift.objects.filter(
            authenticated_user=self.request.user).filter(end__isnull=True)

        return shifts


class NewShiftViewSet(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):

        serializer = NewShiftSerializer(data=request.data)
        serializer.is_valid()
        serializer.create(serializer.validated_data, request)

        return Response(serializer.data)
