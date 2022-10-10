from django.utils import timezone
from escpos.printer import Network
from pos.models.stock import Order, OrderLine, Item
from pos.models.printer import Printer

from django.conf import settings

PAD_SIZE = 25


def item_to_string(name, price):
    pad_size = PAD_SIZE - len(name)
    pad = "" if pad_size <= 0 else " " * pad_size
    return name + pad + ": " + str(price) + ",- "


def print_receipt(order_id):
    order = Order.objects.get(pk=order_id)
    printer_config = Printer.objects.get(user=order.authenticated_user)
    printer = Network(printer_config.address, port=printer_config.port)
    try:
        order_lines = order.orderlines.all()

        printer.hw('INIT')
        printer.set(align='center')
        print_cp865(printer, settings.EVENT_NAME)
        printer.set(align='left')
        printer.ln(1)

        print_cp865(printer, settings.COMPANY_NAME)
        print_cp865(printer, "Adresse: " + settings.COMPANY_ADDRESS)
        print_cp865(printer, "OrgNr:   " + settings.COMPANY_ORG_NR)
        print_cp865(printer, "Dato:    " + timezone.localtime(order.date).strftime("%d.%m.%Y %H:%M:%S"))
        printer.ln(1)

        total = 0
        for order_line in order_lines:
            total += order_line.price
            print_cp865(printer, item_to_string(order_line.item.name, order_line.price))

        print_cp865(printer, item_to_string("MVA", 0))
        printer.set(underline=True, bold=True)
        print_cp865(printer, item_to_string("Total", total))
        printer.ln(5)
        printer.cut(mode='PART')
    finally:
        printer.close()


def print_pickup_receipts(order_id):
    order = Order.objects.get(pk=order_id)
    printer_config = Printer.objects.get(user=order.authenticated_user)
    printer = Network(printer_config.address, port=printer_config.port)
    try:
        order_lines = order.orderlines.all()

        printer.hw('INIT')
        for order_line in order_lines:
            ingredients = order_line.ingredients.all()
            print_order(printer, order_line.id, order.date, order_line.message, order_line.item, ingredients)
    finally:
        printer.close()


def print_cp865(printer, text, new_line=True):
    printer._raw(b'\x1B\x74\x05')
    printer._raw(text.encode('CP865'))
    if new_line:
        printer.ln(1)


def print_order(printer, id, date, message, item, ingredients):
    printer.set(align='center', double_height=True, double_width=True)
    printer.textln("Ordre: " + str(id))
    printer.set(align='center', double_height=False, double_width=False)
    printer.ln(1)
    printer.set(align='left', double_height=False, double_width=False)
    timezone.activate('Europe/Oslo')
    printer.textln('Dato: ' + timezone.localtime(date).strftime("%d.%m.%Y %H:%M:%S"))
    timezone.deactivate()
    printer.ln(1)
    print_cp865(printer, item.name, True)
    for ingredient in ingredients:
        print_cp865(printer, "    " + ingredient.name)
    printer.ln(1)
    if message is not None and len(message) > 0:
        print_cp865(printer, message)
    printer.ln(3)
    printer.cut(mode='PART')
