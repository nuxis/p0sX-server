from pos.models.stock import Category, Ingredient, Item, Order, OrderLine, Purchase
from pos.models.user import User

from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'price', 'stock', 'barcode', 'category', 'can_have_ingredients', 'image')


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ('id', 'ingredients', 'item')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'stock', 'price')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'date', 'state', 'payment_method')


class PurchaseSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=False)
    lines = OrderLineSerializer(many=True)

    def create(self, validated_data):
        user = validated_data.get('user')
        if user:
            order = Order.create(User.objects.get(pk=user))
        else:
            order = Order.create(None)
        order.save()

        prepared_order = False

        for line in validated_data.get('lines'):
            l = OrderLine.create(line.get('item'), order)
            l.save()
            for ingredient in line.get('ingredients'):
                l.ingredients.add(ingredient)
            l.save()

            if l.item.created_in_the_kitchen:
                prepared_order = True

        # Set the order to DONE if its not going to the kitchen
        if not prepared_order:
            order.state = 2
            order.save()

        return Purchase(order)
