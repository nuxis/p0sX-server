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

    def create(self, validated_data):
        card = validated_data.get('card')
        payment_method = validated_data.get('payment_method')
        if card:
            order = Order.create(User.objects.get(card=card), payment_method)
        else:
            order = Order.create(None, payment_method)
        order.save()

        prepared_order = False

        for line_dict in validated_data.get('lines'):
            ingredients = line_dict.get('ingredients')
            item = line_dict.get('item')
            price = item.price + sum(i.price for i in ingredients)

            line = OrderLine.create(item, order, price)
            line.save()
            line.ingredients.add(*ingredients)
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
