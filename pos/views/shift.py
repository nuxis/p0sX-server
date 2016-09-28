from django.utils import timezone
from rest_framework.response import Response

from datetime import datetime

from pos.models.shift import Shift

from pos.serializers.shift import ShiftSerializer

from rest_framework import viewsets


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

    def create(self, request, *args, **kwargs):
        # if Shift.objects.count() > 0:
        #     current_shift = Shift.objects.latest('id')
        #     current_shift.end = timezone.now()
        #     current_shift.save()
        #     # TODO: Calculate how much money should be in the register
        # return super(ShiftViewSet, self).create(request, args, kwargs)

        open_shifts = Shift.objects.filter(
            authenticated_user=self.request.user).filter(end__isnull=True)

        for shift in open_shifts:
            shift.end = datetime.now()

        new_shift = Shift(authenticated_user=self.request.user)

        serializer = ShiftSerializer(new_shift)

        return Response(serializer.data)


class CurrentShiftViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShiftSerializer

    def get_queryset(self):
        shifts = Shift.objects.filter(
            authenticated_user=self.request.user).filter(end__isnull=True)

        return shifts
