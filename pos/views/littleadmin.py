import datetime
import itertools

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Case, IntegerField, Sum, When
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from ..forms import AddCreditForm, AddUserForm, ChangeCreditForm, CheckCreditForm, CreditStatsForm
from ..models.shift import Shift
from ..models.stock import Item, OrderLine, Order
from ..models.user import User, CreditUpdate
from ..serializers.shift import ShiftSerializer


def check_credit(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']
            user = User.objects.filter(card=card)

            if not user:
                return HttpResponseRedirect(reverse_lazy('littleadmin:check'))

            orders = Order.objects.filter(user_id=user[0].id).order_by('-date')[0:3]

            return render(request, 'pos/credit_check.djhtml', {
                'form': CheckCreditForm(),
                'orders': get_order_details(orders),
                'table': True,
                'used': user[0].used,
                'credit': user[0].credit,
                'left': user[0].left
            })
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:check'))
    else:
        return render(request, 'pos/credit_check.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


def get_order_details(orders):
    value = "<ul>\n"
    for order in orders:
        value += f"<li><b>{order.info}</b>\n"
        value += "<ul style='margin-left: 15px'>\n"

        for line in order.orderlines.all():
            value += f"<li>{line}</li>\n"
        value += "</ul>\n"
    value += "</ul>\n"
    return value


@login_required
def credit_overview(request):
    bought = OrderLine.objects.all().exclude(order__user__isnull=True).values('order__user').annotate(used=Sum('price'))
    users = User.objects.all().values()
    for user in users:
        for b in bought:
            user['used'] = 0
            user['left'] = 0
            if b['order__user'] == user['id']:
                user['used'] = b['used']
                user['left'] = user['credit'] - user['used']
                break

    context = {
        'users': users
    }

    return render(request, 'pos/credit_overview.djhtml', context)


@login_required
def crew_report(request):
    crew = User.objects.filter(crew=True)

    credit_result = []
    for c in crew:
        items = OrderLine.objects.filter(order__user=c).values('item__name')\
            .annotate(total=Sum('price'),
                      number=Sum(Case(When(price__gt=0, then=1), default=-1, output_field=IntegerField())))

        total = sum(map(lambda x: x['total'], items))
        credit_result.append({'card': c.card, 'lines': items, 'name': c.first_name + ' ' + c.last_name, 'total': total})

    return render(request, 'pos/crew_report.djhtml', {'crew': credit_result})


@login_required
def credit_edit(request, card=None):
    if request.POST:
        form = ChangeCreditForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data['credit']
            user = get_object_or_404(User, card=card)

            user.credit = credit
            user.save()
            return HttpResponseRedirect(reverse_lazy('littleadmin:overview'))
    else:
        user = get_object_or_404(User, card=card)
        form = ChangeCreditForm(instance=user)

        return render(request, 'pos/credit_edit.djhtml', {'form': form, 'target': user})


@login_required
def sale_overview(request):
    order_lines = OrderLine.objects.all().values('item__id', 'order__payment_method')\
        .annotate(total=Sum('price'),
                  sold=Sum(Case(When(price__gt=0, then=1), default=-1, output_field=IntegerField())))

    items = Item.objects.all().values('name', 'category__name', 'id', 'price')
    total = {'cash': 0, 'credit': 0, 'total': 0}

    overview = {}

    for item in items:
        per_payment_method = order_lines.filter(item_id=item['id'])
        try:
            credit = per_payment_method.filter(order__payment_method=1)[0]
        except IndexError:
            credit = {'sold': 0, 'total': 0}
        try:
            cash = per_payment_method.filter(order__payment_method=0)[0]
        except IndexError:
            cash = {'sold': 0, 'total': 0}
        item['cash'] = cash['total']
        item['credit'] = credit['total']
        item['sold'] = cash['sold'] + credit['sold']
        item['total'] = item['cash'] + item['credit']

        if item['price'] < 0:
            item['sold'] *= -1

        if item['category__name'] in overview.keys():
            overview[item['category__name']].append(item)
        else:
            overview[item['category__name']] = [item]

        total['cash'] += item['cash']
        total['credit'] += item['credit']
        total['total'] += item['total']

    shifts = ShiftSerializer(Shift.objects.all(), many=True)
    return render(request, 'pos/sale_overview.djhtml', {'overview': overview, 'shifts': shifts.data, 'total': total})


@permission_required("pos.update_credit")
def scan_user_card(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            user = User.objects.filter(card=card)

            if not user:
                return redirect('littleadmin:add_user', card=card)

            return redirect('littleadmin:add_user_credit', card=card)
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:scan_user_card'))
    else:
        return render(request, 'pos/scan_card.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


@permission_required('pos.update_credit')
def add_user_credit(request, card=None):
    if request.POST:
        form = AddCreditForm(request.POST)

        if form.is_valid():
            credit = form.cleaned_data['credit']
            user = get_object_or_404(User, card=card)

            if user.is_crew:
                messages.error(request, "You cannot change the credit of Crew")
                return redirect('littleadmin:scan_user_card')

            try:
                amount = int(credit)
            except ValueError:
                return redirect('littleadmin:add_user_credit', card)

            if amount > 1000:
                messages.error(request, "The maximum credit that can be added at once is 1000.<br />Add multiple times if more is needed")
                return redirect('littleadmin:add_user_credit', card)

            return redirect('littleadmin:verify_add_credit', user.id, amount)
        else:
            return redirect('littleadmin:add_user_credit', card)
    else:
        user = get_object_or_404(User, card=card)

        if user.is_crew:
            messages.error(request, "You cannot change the credit of Crew")
            return redirect('littleadmin:scan_user_card')

        form = AddCreditForm()

        return render(request, 'pos/add_credit.djhtml', {'form': form, 'target': user})


@permission_required('pos.update_credit')
def add_user(request, card=None):
    if request.POST:
        form = AddUserForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.create(card, 0, first_name, last_name, '', '')

            user.save()
            return redirect('littleadmin:scan_user_card')
        else:
            messages.error(request, "Failed to add user")
            return HttpResponseRedirect(reverse_lazy('littleadmin:add_user'))
    else:
        form = AddUserForm(initial={'card': card})
        return render(request, 'pos/add_user.djhtml', {
            'form': form
        })


@permission_required('pos.update_credit')
def verify_add_credit(request, user='', amount=''):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            target = get_object_or_404(User, id=int(user))
            card = form.cleaned_data['card']
            crew = User.objects.filter(card=card)

            if not crew or not crew[0].is_crew:
                messages.error(request, "Failed to verify, are you crew?")
                return redirect('littleadmin:verify_add_credit', user, amount)

            target.credit += int(amount)
            target.save()

            update = CreditUpdate.create(target, crew[0], amount)
            update.save()

            messages.success(request, f"Success! Credit set to {target.left}")
            return redirect('littleadmin:scan_user_card')
        else:
            messages.error(request, "Failed to add user")
            return HttpResponseRedirect(reverse_lazy('littleadmin:scan_user_card'))
    else:
        form = CheckCreditForm()
        return render(request, 'pos/verify_add_credit.djhtml', {
            'form': form
        })


def group_credit_updates(date, group_by):
    times = [
        datetime.timedelta(hours=0),
        datetime.timedelta(hours=6),
        datetime.timedelta(hours=12),
        datetime.timedelta(hours=18)
    ]
    seconds = (date.hour * 60 * 60) + (date.minute * 60) + date.second
    seconds /= group_by.total_seconds()

    index = int(seconds)

    timestamp = datetime.datetime.combine(date.date(), datetime.datetime.min.time()) + times[index]

    return timestamp


@login_required()
def add_credit_stats(request):
    if request.POST:
        form = CreditStatsForm(request.POST)
        if not form.is_valid():
            return redirect('littleadmin:add_credit_stats')

        from_time = form.cleaned_data['from_time']
        to_time = form.cleaned_data['to_time']

        updates = CreditUpdate.objects.filter(timestamp__lte=to_time, timestamp__gte=from_time)
        orders = Order.objects.filter(date__lte=to_time, date__gte=from_time)

        total_out = sum([x.sum for x in orders])

        total = sum([x.amount for x in updates])

        form = CreditStatsForm(initial={'from_time': f"{from_time:%Y-%m-%dT%H:%M}", 'to_time': f"{to_time:%Y-%m-%dT%H:%M}"})
    else:
        total = 0
        total_out = 0
        updates = []
        orders = []
        form = CreditStatsForm()

    return render(request, 'pos/add_credit_stats.djhtml', {
        'updates': updates,
        'orders': orders,
        'total': total,
        'total_out': total_out,
        'form': form
    })
