from django.shortcuts import get_object_or_404

from pos.models.stock import Category, Item, ItemIngredient, Order, OrderLine, Purchase
from pos.models.user import User

from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ItemIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    price = serializers.ReadOnlyField(source='ingredient.price')
    stock = serializers.ReadOnlyField(source='ingredient.stock')

    class Meta:
        model = ItemIngredient
        fields = ('id', 'default', 'name', 'price', 'stock')


class ItemSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()

    @staticmethod
    def get_ingredients(obj):
        item_ingredients = ItemIngredient.objects.filter(item=obj.pk)
        if item_ingredients:
            serializer = ItemIngredientsSerializer(item_ingredients, many=True)
            return serializer.data
        else:
            return []

    class Meta:
        model = Item
        fields = ('id', 'name', 'price', 'stock', 'barcode', 'category', 'image', 'ingredients')


class OrderLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderLine
        fields = ('id', 'ingredients', 'item')
        depth = 1


class OrderSerializer(serializers.ModelSerializer):
    orderlines = OrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'date', 'state', 'payment_method', 'orderlines')


class CreditCheckSerializer(serializers.Serializer):
    used = serializers.IntegerField()
    credit_limit = serializers.IntegerField()
    left = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PurchaseSerializer(serializers.Serializer):
    payment_method = serializers.IntegerField(required=True)
    card = serializers.IntegerField(required=False)
    lines = OrderLineSerializer(many=True)
    message = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        card = validated_data.get('card')
        payment_method = validated_data.get('payment_method')
        message = validated_data.get('message')
        if card:
            user = get_object_or_404(User.objects.all(), card=card)
            order = Order.create(user, payment_method, message)
        else:
            order = Order.create(None, payment_method, message)
        order.save()

        prepared_order = False

        for line_dict in validated_data.get('lines'):
            ingredients = line_dict.get('ingredients')
            item = line_dict.get('item')
            price = item.price + sum(i.price for i in ingredients)

            line = OrderLine.create(item, order, price)
            line.save()
            if len(ingredients):
                line.ingredients.set((i.pk for i in ingredients))
                line.save()

            if line.item.created_in_the_kitchen:
                prepared_order = True

        # Set the order to DONE if its not going to the kitchen
        if not prepared_order:
            order.state = 2
            order.save()

        return Purchase(order)

    def update(self, instance, validated_data):
        pass
