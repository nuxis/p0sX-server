from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from pos.models.stock import Category, CreditCheck, Discount, Item, Order, OrderLine, Purchase
from pos.serializers.stock import (CategorySerializer,
                                   CreditCheckSerializer,
                                   DiscountSerializer,
                                   ItemSerializer,
                                   OrderLineSerializer,
                                   OrderSerializer,
                                   PurchaseSerializer)
from pos.models.crew import Crew
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
            return Response(serializer.data)
        else:
            error = {'detail': 'Invalid data'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class CreditCheckViewSet(viewsets.ViewSet):

    @staticmethod
    def retrieve(request, pk=None):
        crews = Crew.objects.all()
        crew = get_object_or_404(crews, card=pk)
        orders = Order.objects.filter(crew=crew)
        orderlines = OrderLine.objects.filter(order__in=orders)

        total = sum(ol.price for ol in orderlines)
        credit_limit = crew.credit

        queryset = CreditCheck(total, credit_limit)
        serializer = CreditCheckSerializer(queryset)
        return Response(serializer.data)
