from pos.models.shift import Shift
from pos.models.stock import Order

from django.utils.timezone import now

from rest_framework import serializers


class ShiftSerializer(serializers.ModelSerializer):
    cash = serializers.SerializerMethodField()
    crew = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField()
    vipps = serializers.SerializerMethodField()
    mcash = serializers.SerializerMethodField()
    mobilepay = serializers.SerializerMethodField()
    izettle = serializers.SerializerMethodField()
    undo = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = ('__all__')
        read_only_fiels = ('end')

    def accumulate_sum(self, obj, payment_method):
        if obj.end:
            orders = Order.objects.filter(
                date__gte=obj.start).filter(date__lte=obj.end).filter(authenticated_user=obj.authenticated_user)
        else:
            orders = Order.objects.filter(
                date__gte=obj.start).filter(authenticated_user=obj.authenticated_user)
        return sum([order.sum for order in orders if order.payment_method == payment_method])

    def get_cash(self, obj):
        return self.accumulate_sum(obj, 0)

    def get_crew(self, obj):
        return self.accumulate_sum(obj, 1)

    def get_card(self, obj):
        return self.accumulate_sum(obj, 2)

    def get_vipps(self, obj):
        return self.accumulate_sum(obj, 3)

    def get_mcash(self, obj):
        return self.accumulate_sum(obj, 4)

    def get_mobilepay(self, obj):
        return self.accumulate_sum(obj, 5)

    def get_izettle(self, obj):
        return self.accumulate_sum(obj, 6)

    def get_undo(self, obj):
        return self.accumulate_sum(obj, 7)


class NewShiftSerializer(serializers.Serializer):

    def create(self, request):
        open_shifts = Shift.objects.filter(
            authenticated_user=request.user).filter(end__isnull=True)

        for shift in open_shifts:
            shift.end = now()
            shift.save()

        new_shift = Shift(authenticated_user=request.user)
        new_shift.save()

        return new_shift
