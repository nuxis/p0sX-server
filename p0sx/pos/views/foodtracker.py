from datetime import timedelta

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from pos.models.stock import Category, FoodLog, Order, OrderLine, PaymentState, OrderState


def get_order_lines(state):
    orders = Order.objects.filter(payment_state=PaymentState.Paid)
    return OrderLine.objects.filter(order__in=orders, state=state)

def active_orders(request):
    # Fetch orders without status ARCHIVED/DONE and order them.
    # TODO: Make it possible to change status from this screen.
    # Important: Update the OrderLines, not the Orders.
    open_orders = Order.objects.filter(state=OrderState.Open, payment_state=PaymentState.Paid).order_by('date')
    processing_orders = Order.objects.filter(state=OrderState.Processing, payment_state=PaymentState.Paid).filter(orderlines__log__state=1).order_by('orderlines__log__timestamp')
    done_orders = Order.objects.filter(state=OrderState.Done, payment_state=PaymentState.Paid).filter(orderlines__log__state=2).order_by('orderlines__log__timestamp')

    return render(request, 'pos/active_orders.djhtml', {
        'open_orders': open_orders,
        'processing_orders': processing_orders,
        'done_orders': done_orders
    })


def production_station(request):
    if request.method == 'GET' and 'done' in request.GET:
        orderline_id = request.GET['done']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Done
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    elif request.method == 'GET' and 'start' in request.GET:
        orderline_id = request.GET['start']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Processing
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        open_orderlines = get_order_lines(OrderState.Open).order_by('order__date')
        processing_orderlines = get_order_lines(OrderState.Processing).filter(log__state=1).order_by('log__timestamp')

        return render(request, 'pos/production_station.djhtml', {
            'open_orderlines': open_orderlines,
            'processing_orderlines': processing_orderlines
        })


def production_station_single(request, category):
    if request.method == 'GET' and 'done' in request.GET:
        orderline_id = request.GET['done']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Done
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    elif request.method == 'GET' and 'start' in request.GET:
        orderline_id = request.GET['start']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Processing
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        open_orderlines = get_order_lines(OrderState.Open).filter(item__category=category).order_by('order__date')
        processing_orderlines = get_order_lines(OrderState.Processing).filter(item__category=category).filter(log__state=1).order_by('log__timestamp')
        category_name = Category.objects.get(pk=category)

        return render(request, 'pos/production_station.djhtml', {
            'open_orderlines': open_orderlines,
            'processing_orderlines': processing_orderlines,
            'category': category_name.name
        })


def production_station_exclude(request, category):
    if request.method == 'GET' and 'done' in request.GET:
        orderline_id = request.GET['done']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Done
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    elif request.method == 'GET' and 'start' in request.GET:
        orderline_id = request.GET['start']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Processing
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        open_orderlines = get_order_lines(OrderState.Open).exclude(item__category=category).order_by('order__date')
        processing_orderlines = get_order_lines(OrderState.Processing).exclude(item__category=category).filter(log__state=1).order_by('log__timestamp')
        category_name = Category.objects.get(pk=category)

        return render(request, 'pos/production_station.djhtml', {
            'open_orderlines': open_orderlines,
            'processing_orderlines': processing_orderlines,
            'category': category_name.name
        })


def delivery_station(request):
    if request.method == 'GET' and 'delivered' in request.GET:
        orderline_id = request.GET['delivered']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = OrderState.Archived
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        processing_orderlines = get_order_lines(OrderState.Processing).filter(log__state=1).order_by('log__timestamp')
        done_orderlines = get_order_lines(OrderState.Done).filter(log__state=2).order_by('log__timestamp')

        return render(request, 'pos/delivery_station.djhtml', {
            'processing_orderlines': processing_orderlines,
            'done_orders': done_orderlines
        })


def delivery_screen(request):
    time_threshold = timezone.now() - timedelta(minutes=5)
    orderlines = get_order_lines(OrderState.Done)

    return render(request, 'pos/delivery_screen.djhtml', {
        'orderlines': orderlines
    })
