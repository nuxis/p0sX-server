from django.shortcuts import get_object_or_404

from pos.models.stock import Category, CreditCheck, Discount, Item, OrderLine, Purchase
from pos.models.user import User
from pos.serializers.stock import CategorySerializer, CreditCheckSerializer, DiscountSerializer, ItemSerializer, \
    Order, OrderLineSerializer, OrderSerializer, PurchaseSerializer

from rest_framework import viewsets
from rest_framework.response import Response


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OrderLineViewSet(viewsets.ModelViewSet):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(active=True)
    serializer_class = ItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_fields = ('state',)


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
        serializer = PurchaseSerializer(data=request.data)

        if serializer.is_valid():
            purchase = serializer.create(serializer.validated_data)
            serializer = PurchaseSerializer(purchase)
        else:
            print(serializer.errors)

        return Response(serializer.data)


class CreditCheckViewSet(viewsets.ViewSet):
    @staticmethod
    def retrieve(request, pk=None):
        users = User.objects.all()
        user = get_object_or_404(users, card=pk)
        orders = Order.objects.filter(customer=user)
        orderlines = OrderLine.objects.filter(order__in=orders)

        total = sum(ol.price for ol in orderlines)
        credit_limit = user.credit

        queryset = CreditCheck(total, credit_limit)
        serializer = CreditCheckSerializer(queryset)
        return Response(serializer.data)
