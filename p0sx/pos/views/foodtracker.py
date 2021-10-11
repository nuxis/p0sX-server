from datetime import timedelta

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from pos.models.stock import Category, FoodLog, Order, OrderLine


def active_orders(request):
    # Fetch orders without status ARCHIVED/DONE and order them.
    # TODO: Make it possible to change status from this screen.
    # Important: Update the OrderLines, not the Orders.
    open_orders = Order.objects.filter(state=0).order_by('date')
    processing_orders = Order.objects.filter(state=1).filter(orderlines__log__state=1).order_by('orderlines__log__timestamp')
    done_orders = Order.objects.filter(state=2).filter(orderlines__log__state=2).order_by('orderlines__log__timestamp')

    return render(request, 'pos/active_orders.djhtml', {
        'open_orders': open_orders,
        'processing_orders': processing_orders,
        'done_orders': done_orders
    })


def production_station(request):
    if request.method == 'GET' and 'done' in request.GET:
        orderline_id = request.GET['done']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = 2
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    elif request.method == 'GET' and 'start' in request.GET:
        orderline_id = request.GET['start']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = 1
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        open_orderlines = OrderLine.objects.filter(state=0).order_by('order__date')
        processing_orderlines = OrderLine.objects.filter(state=1).filter(log__state=1).order_by('log__timestamp')

        return render(request, 'pos/production_station.djhtml', {
            'open_orderlines': open_orderlines,
            'processing_orderlines': processing_orderlines
        })


def production_station_single(request, category):
    if request.method == 'GET' and 'done' in request.GET:
        orderline_id = request.GET['done']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = 2
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    elif request.method == 'GET' and 'start' in request.GET:
        orderline_id = request.GET['start']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = 1
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        open_orderlines = OrderLine.objects.filter(state=0).filter(item__category=category).order_by('order__date')
        processing_orderlines = OrderLine.objects.filter(state=1).filter(item__category=category).filter(log__state=1).order_by('log__timestamp')
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
        orderline.state = 2
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    elif request.method == 'GET' and 'start' in request.GET:
        orderline_id = request.GET['start']
        orderline = OrderLine.objects.get(pk=orderline_id)
        orderline.state = 1
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        open_orderlines = OrderLine.objects.filter(state=0).exclude(item__category=category).order_by('order__date')
        processing_orderlines = OrderLine.objects.filter(state=1).exclude(item__category=category).filter(log__state=1).order_by('log__timestamp')
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
        orderline.state = 3
        orderline.save()
        url = request.build_absolute_uri(request.path)
        return HttpResponseRedirect(url)

    else:
        processing_orderlines = OrderLine.objects.filter(state=1).filter(log__state=1).order_by('log__timestamp')
        done_orderlines = OrderLine.objects.filter(state=2).filter(log__state=2).order_by('log__timestamp')

        return render(request, 'pos/delivery_station.djhtml', {
            'processing_orderlines': processing_orderlines,
            'done_orders': done_orderlines
        })


def delivery_screen(request):
    time_threshold = timezone.now() - timedelta(minutes=5)
    orderlines = OrderLine.objects.filter(state=2)

    return render(request, 'pos/delivery_screen.djhtml', {
        'orderlines': orderlines
    })
