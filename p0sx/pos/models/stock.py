from datetime import timedelta
from enum import IntEnum

from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class OrderState(IntEnum):
    Open = 0,
    Processing = 1,
    Done = 2,
    Archived = 3

class PaymentMethod(IntEnum):
    Cash = 0,
    Credit = 1,
    Card = 2,
    Vipps = 3,
    Prepaid = 4,
    Undo = 7

class PaymentState(IntEnum):
    Paid = 0,
    Pending = 1,
    Failed = 2,
    Cancelled = 3

ORDER_STATE = (
    (int(OrderState.Open), 'OPEN'),
    (int(OrderState.Processing), 'PROCESSING'),
    (int(OrderState.Done), 'DONE'),
    (int(OrderState.Archived), 'ARCHIVED')
)

PAYMENT_METHOD = (
    (int(PaymentMethod.Cash), 'CASH'),
    (int(PaymentMethod.Credit), 'CREDIT'),
    (int(PaymentMethod.Card), 'CARD'),
    (int(PaymentMethod.Vipps), 'VIPPS'),
    (int(PaymentMethod.Prepaid), 'PREPAID'),
    (int(PaymentMethod.Undo), 'UNDO')
)

PAYMENT_STATE = (
    (int(PaymentState.Paid), 'PAID'),
    (int(PaymentState.Pending), 'PENDING'),
    (int(PaymentState.Failed), 'FAILED'),
    (int(PaymentState.Cancelled), 'CANCELLED')
)


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    price = models.SmallIntegerField()
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    barcode = models.CharField(max_length=255)
    active = models.BooleanField(blank=False, default=True, db_index=True)
    image = models.ImageField(upload_to='', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_in_the_kitchen = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return self.name


class ItemIngredient(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    default = models.BooleanField(default=False)
    exclusive = models.BooleanField(default=False)

    def __unicode__(self):
        return self.item.name + (' has ' if self.default else ' can have ') + self.ingredient.name

    def __str__(self):
        return self.item.name + (' has ' if self.default else ' can have ') + self.ingredient.name


class Order(models.Model):
    user = models.ForeignKey(
        'User', related_name='purchasing_user', blank=True, null=True, db_index=True, on_delete=models.CASCADE)
    cashier = models.ForeignKey('User', related_name='cashier', on_delete=models.CASCADE)
    authenticated_user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    state = models.SmallIntegerField(default=0, choices=ORDER_STATE)
    payment_method = models.SmallIntegerField(default=0, choices=PAYMENT_METHOD, db_index=True)
    payment_state = models.SmallIntegerField(default=0, choices=PAYMENT_STATE, db_index=True)
    payment_reference = models.CharField(max_length=256, blank=True)
    message = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return str(self.user) + ' ' + self.date.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def info(self):
        localtime = self.date + timedelta(hours=2)
        return f"{localtime:%Y-%m-%d %H:%M:%S} - {self.sum},-"

    @classmethod
    def create(cls, user, cashier, authenticated_user, payment_method, message):
        order = cls(user=user,
                    cashier=cashier,
                    authenticated_user=authenticated_user,
                    payment_method=payment_method,
                    message=message)

        return order

    @property
    def sum(self):
        return sum(line.price for line in self.orderlines.all())


class OrderLine(models.Model):
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    item = models.ForeignKey(Item, db_index=True, on_delete=models.CASCADE)
    price = models.IntegerField()
    order = models.ForeignKey(Order, related_name='orderlines', db_index=True, on_delete=models.CASCADE)
    state = models.SmallIntegerField(choices=ORDER_STATE, default=0)
    message = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        s = self.item.name

        actual_ingredients = self.ingredients.all()
        print(actual_ingredients)
        if len(actual_ingredients) > 0:
            s += ' med '
            s += ', '.join([str(item).lower() for item in actual_ingredients])

        return s

    @classmethod
    def create(cls, item, order, price, message):
        line = cls(item=item, order=order, price=price, message=message)
        return line


class Purchase:

    def __init__(self, order):
        self.id = order.pk
        self.order = order
        self.user = order.user_id
        self.lines = OrderLine.objects.filter(order=order)
        self.payment_method = order.payment_method
        self.message = order.message
        self.card = '' if order.user is None else order.user.card
        self.undo = order.payment_method == PaymentMethod.Undo
        self.cashier_card = order.cashier.card
        self.state = order.state
        self.payment_state = order.payment_state

    def __str__(self):
        s = str(self.order)
        for line in self.lines:
            s += '\n' + str(line)

        return s


class CreditCheck:

    def __init__(self, used, user):
        self.used = used
        self.credit_limit = user.credit
        self.left = user.credit - used
        self.is_crew = user.is_crew


class Discount(models.Model):
    payment_method = models.SmallIntegerField(
        choices=PAYMENT_METHOD, default=0)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    expression = models.TextField()


class FoodLog(models.Model):
    orderline = models.ForeignKey(OrderLine, related_name='log', on_delete=models.PROTECT)
    state = models.SmallIntegerField(choices=ORDER_STATE, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('orderline', 'state')

    def __str__(self):
        return '{} set state {} at {}'.format(self.orderline, self.get_state_display(), self.timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    @receiver(post_save, sender=OrderLine)
    def create_logline(sender, instance, **kwargs):
        if instance.item.created_in_the_kitchen:
            FoodLog.objects.get_or_create(orderline=instance, state=instance.state)

            order_line = OrderLine.objects.filter(order=instance.order).exclude(item__created_in_the_kitchen=False)
            order = Order.objects.filter(pk=instance.order.id)
            processing = 0
            done = 0
            archived = 0
            for line in order_line:
                if line.state == OrderState.Processing:
                    processing += 1
                elif line.state == OrderState.Done:
                    done += 1
                elif line.state == OrderState.Archived:
                    archived += 1
            if processing >= 1:
                order.update(state=OrderState.Processing)
            if done == order_line.count():
                order.update(state=OrderState.Done)
            if archived == order_line.count():
                order.update(state=OrderState.Archived)
