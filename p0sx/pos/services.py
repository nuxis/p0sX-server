from time import sleep
from django.utils import timezone
from escpos.printer import Network
from pos.models.stock import Order, OrderLine, Item
from pos.models.printer import Printer


def sleep_and_print(secs):
    sleep(secs)
    print("Task ran!")


def print_pickup_receipts(order_id):
    order = Order.objects.get(pk=order_id)
    printer_config = Printer.objects.get(user=order.authenticated_user)
    printer = Network(printer_config.address, port=printer_config.port)
    order_lines = order.orderlines.all()

    for order_line in order_lines:
        ingredients = order_line.ingredients.all()
        print_order(printer, order_line.id, order.date, order_line.message, order_line.item, ingredients)


def print_order(printer, id, date, message, item, ingredients):

    printer.hw('INIT')
    printer.set(align='center', double_height=True, double_width=True)
    printer.textln("Ordre: " + str(id))
    printer.set(align='center', double_height=False, double_width=False)
    printer.ln(1)
    printer.set(align='left', double_height=False, double_width=False)
    timezone.activate('Europe/Oslo')
    printer.textln('Dato: ' + timezone.localtime(date).strftime("%d.%m.%Y %H:%M:%S"))
    timezone.deactivate()
    printer.ln(1)
    printer.textln(item.name)
    for ingredient in ingredients:
        printer.textln("    " + ingredient.name)
    printer.ln(1)
    if len(message) > 0:
        printer.textln(message)
    printer.ln(4)
    printer.cut(mode='PART')
    printer.close()
