from django.db import models

from .user import User

ORDER_STATE = (
    (0, 'OPEN'),
    (1, 'IN_PROGRESS'),
    (2, 'DELIVERED')
)

PAYMENT_METHOD = (
    (0, 'CASH'),
    (1, 'CREW'),
    (2, 'CARD'),
    (3, 'VIPPS'),
    (4, 'MCASH'),
    (5, 'MOBILEPAY'),
    (6, 'IZETTLE')
)


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    stock = models.IntegerField()
    barcode = models.CharField(max_length=255)
    image = models.ImageField(upload_to='', blank=False)
    category = models.ForeignKey(Category)
    can_have_ingredients = models.BooleanField(blank=False, default=False)
    created_in_the_kitchen = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    state = models.SmallIntegerField(default=0, choices=ORDER_STATE)
    payment_method = models.SmallIntegerField(default=0, choices=PAYMENT_METHOD)
    message = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return str(self.customer) + ' ' + self.date.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def create(cls, customer):
        order = cls(customer=customer)

        return order


class OrderLine(models.Model):
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    item = models.ForeignKey(Item)
    order = models.ForeignKey(Order)

    def __str__(self):
        s = self.item.name

        if len(self.ingredients.all()) > 0:
            s += ' med '
            s += ', '.join([str(item).lower() for item in self.ingredients.all()])

        return s

    @classmethod
    def create(cls, item, order):
        line = cls(item=item, order=order)
        return line


class Purchase:
    def __init__(self, order):
        self.order = order
        self.user = order.customer_id
        self.lines = OrderLine.objects.filter(order=order)

    def __str__(self):
        s = str(self.order)
        for line in self.lines:
            s += '\n' + str(line)

        return s
