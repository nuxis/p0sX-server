from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


from pos.models.stock import Category, CreditCheck, Discount, Item, Order, OrderLine, Purchase
from pos.models.user import User
from pos.serializers.stock import (CategorySerializer,
                                   CreditCheckSerializer,
                                   DiscountSerializer,
                                   ItemSerializer,
                                   OrderLineSerializer,
                                   OrderSerializer,
                                   PurchaseSerializer)

from rest_framework import status, viewsets
from rest_framework.response import Response


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(hidden=False)
    serializer_class = CategorySerializer


class OrderLineViewSet(viewsets.ModelViewSet):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(active=True).order_by('name')
    serializer_class = ItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_fields = ['state']


class PurchaseViewSet(viewsets.ViewSet):

    def list(self, request):
        orders = Order.objects.all()
        queryset = []
        for order in orders:
            queryset.append(Purchase(order))
        serializer = PurchaseSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        orders = Order.objects.all()
        order = get_object_or_404(orders, pk=pk)
        queryset = Purchase(order)
        serializer = PurchaseSerializer(queryset)
        return Response(serializer.data)

    def create(self, request):
        try:
            serializer = PurchaseSerializer(data=request.data)

            if serializer.is_valid():
                purchase = serializer.create(serializer.validated_data, request)
                serializer = PurchaseSerializer(purchase)
                return Response(serializer.data)
            else:
                error = {'detail': 'Invalid data'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error = {'detail': e.message}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class CreditCheckViewSet(viewsets.ViewSet):

    @staticmethod
    def retrieve(request, pk=None):
        users = User.objects.all()
        user = get_object_or_404(users, card=pk)
        orders = Order.objects.filter(user=user)
        orderlines = OrderLine.objects.filter(order__in=orders)

        total = sum(ol.price for ol in orderlines)
        credit_limit = user.credit

        queryset = CreditCheck(total, credit_limit)
        serializer = CreditCheckSerializer(queryset)
        return Response(serializer.data)
