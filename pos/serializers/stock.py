from pos.models.stock import *
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
    card = serializers.IntegerField(required=False)
    lines = OrderLineSerializer(many=True)

    def create(self, validated_data):
        card = validated_data.get('card')
        if card:
            order = Order.create(User.objects.get(card=card))
        else:
            order = Order.create(None)
        order.save()

        prepared_order = False

        for line in validated_data.get('lines'):
            l = OrderLine.create(line.get('item'), order)
            l.save()
            l.ingredients.add(*(validated_data.get('ingredients') or []))
            l.save()

            if l.item.created_in_the_kitchen:
                prepared_order = True

        # Set the order to DONE if its not going to the kitchen
        if not prepared_order:
            order.state = 2
            order.save()

        return Purchase(order)

    def update(self, instance, validated_data):
        pass
