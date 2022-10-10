from datetime import timedelta

from django.utils.timezone import now

from pos.models.shift import Shift
from pos.models.stock import Order
from pos.models.user import User

from rest_framework import serializers


class ShiftSerializer(serializers.ModelSerializer):
    cash = serializers.SerializerMethodField()
    credit = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField()
    vipps = serializers.SerializerMethodField()
    prepaid = serializers.SerializerMethodField()
    mobilepay = serializers.SerializerMethodField()
    izettle = serializers.SerializerMethodField()
    undo = serializers.SerializerMethodField()
    shift_name = serializers.SerializerMethodField()

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

    def get_shift_name(self, obj):
        local_start = obj.start + timedelta(hours=2)
        return obj.authenticated_user.username + ' - Started: ' + local_start.strftime('%A %H:%M:%S')

    def get_cash(self, obj):
        return self.accumulate_sum(obj, 0)

    def get_credit(self, obj):
        return self.accumulate_sum(obj, 1)

    def get_card(self, obj):
        return self.accumulate_sum(obj, 2)

    def get_vipps(self, obj):
        return self.accumulate_sum(obj, 3)

    def get_prepaid(self, obj):
        return self.accumulate_sum(obj, 4)

    def get_mobilepay(self, obj):
        return self.accumulate_sum(obj, 5)

    def get_izettle(self, obj):
        return self.accumulate_sum(obj, 6)

    def get_undo(self, obj):
        return self.accumulate_sum(obj, 7)


class NewShiftSerializer(serializers.Serializer):
    card = serializers.CharField(required=True)

    def create(self, validated_data, request):
        card = validated_data.get('card')
        user = User.objects.get(card__iexact=card)

        open_shifts = Shift.objects.filter(
            authenticated_user=request.user).filter(end__isnull=True)

        for shift in open_shifts:
            shift.end = now()
            shift.save()

        new_shift = Shift(authenticated_user=request.user, user=user)
        new_shift.save()

        return new_shift
