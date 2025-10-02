from django.core.exceptions import ValidationError, ObjectDoesNotExist

from pos.models.stock import Category, Discount, Ingredient, Item, ItemIngredient, Order, OrderLine, Purchase, OrderState, PaymentMethod, PaymentState
from pos.models.user import User
from pos.models.sumup_cloud import SumupReader

from django_q.tasks import async_task

from rest_framework import serializers
from rest_framework.exceptions import APIException

from pos.service import sumup


class DiscountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discount
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name')


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
        fields = ('id', 'default', 'exclusive', 'name', 'price', 'stock')


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
        fields = ('id', 'name', 'price', 'stock', 'barcode',
                  'category', 'image', 'ingredients', 'created_in_the_kitchen')


class SimpleItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'name', 'created_in_the_kitchen')


class ItemField(serializers.Field):

    def to_representation(self, obj):
        serializer = SimpleItemSerializer(obj)
        return serializer.data

    def to_internal_value(self, data):
        return Item.objects.get(pk=data)


class IngredientField(serializers.Field):

    def to_representation(self, obj):
        serializer = IngredientSerializer(obj, many=True)
        return serializer.data

    def to_internal_value(self, data):
        return Ingredient.objects.filter(pk__in=data)


class OrderLineSerializer(serializers.ModelSerializer):
    item = ItemField()
    ingredients = IngredientField()
    message = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = OrderLine
        fields = ('id', 'ingredients', 'item', 'message', 'state')


class OrderSerializer(serializers.ModelSerializer):
    orderlines = OrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'date', 'state',
                  'payment_method', 'orderlines', 'payment_state')


class CreditCheckSerializer(serializers.Serializer):
    used = serializers.IntegerField()
    credit_limit = serializers.IntegerField()
    left = serializers.IntegerField()
    is_crew = serializers.BooleanField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PurchaseSerializer(serializers.Serializer):
    payment_method = serializers.IntegerField(required=True)
    card = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    cashier_card = serializers.CharField(required=True)
    lines = OrderLineSerializer(many=True)
    message = serializers.CharField(required=False, allow_blank=True)
    id = serializers.IntegerField(required=False)
    undo = serializers.BooleanField()
    state = serializers.IntegerField(required=False)
    payment_state = serializers.IntegerField(required=False)

    def create(self, validated_data, request):
        card = validated_data.get('card')

        cashier_card = validated_data.get('cashier_card')
        cashier = User.objects.get(card__iexact=cashier_card)

        authenticated_user = request.user

        payment_method = validated_data.get('payment_method')
        message = validated_data.get('message')
        undo = validated_data.get('undo')
        order_lines = validated_data.get('lines')

        order_total = 0
        for order_line in order_lines:
            ingredients = order_line.get('ingredients')
            item = order_line.get('item')

            order_total += item.price + sum(i.price for i in ingredients)
            count = len([line for line in order_lines if line.get('item').id == item.id])
            if item.stock < count:
                raise ValidationError('{} is not in stock'.format(item.name))

        user = None
        if card:
            try:
                user = User.objects.get(card__iexact=card)
            except ObjectDoesNotExist:
                user = User(
                    card=card,
                    first_name="Navn",
                    last_name="Navnesen",
                    phone="",
                    crew="",
                    role="",
                    email="",
                    credit=0,
                    is_crew=False
                )
                user.save()
            payment_method = PaymentMethod.Credit if user.is_crew else PaymentMethod.Prepaid
            #if payment_method != 1 and crew.is_crew:
            #    raise ValidationError('The user is marked as crew but payment method was not CREDIT')
            #if payment_method == 1 and not crew.is_crew:
            #    raise ValidationError('Only users marked as crew can use payment method CREDIT')

            user_orders = Order.objects.filter(user=user)
            user_order_lines = OrderLine.objects.filter(order__in=user_orders)

            total = sum(ol.price for ol in user_order_lines)
            credit_left = user.credit - total
            if credit_left < order_total:
                if user.is_crew:
                    raise ValidationError('Not enough credit left on card')
                else:
                    payment_method = PaymentMethod.Card

        sumup_reader = None
        if payment_method == PaymentMethod.Card:
            try:
                sumup_reader = SumupReader.objects.get(user=authenticated_user)
            except SumupReader.DoesNotExist:
                raise APIException()

        order = Order.create(user, cashier, authenticated_user, payment_method, message)
        order.payment_state = PaymentState.Pending if payment_method == PaymentMethod.Card else PaymentState.Paid
        order.save()

        prepared_order = False

        for line_dict in order_lines:
            ingredients = line_dict.get('ingredients')
            item = line_dict.get('item')
            message = line_dict.get('message')

            price = item.price + sum(i.price for i in ingredients)
            price = price * -1 if undo else price

            line = OrderLine.create(item, order, price, message)
            line.save()
            if len(ingredients):
                line.ingredients.set((i.pk for i in ingredients))
                line.save()

            if line.item.created_in_the_kitchen and not undo:
                prepared_order = True
            else:
                line.state = OrderState.Archived
                line.save()

        # Set the order to ARCHIVED if its not going to the kitchen
        if not prepared_order:
            order.state = OrderState.Archived
            order.save()

        if order.payment_method == PaymentMethod.Card:
            sumup.init_order_card_payment(order, reader_id=sumup_reader.reader_id)
        elif prepared_order:
            async_task("pos.services.print_pickup_receipts", order.id,
                       task_name='Pickup receipts for order {id}'.format(id=order.id))

        return Purchase(order)

    def update(self, instance, validated_data):
        pass
