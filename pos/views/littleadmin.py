from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Case, IntegerField, Sum, When
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy

from ..forms import AddUserForm, ChangeCreditForm, CheckCreditForm
from ..models.shift import Shift
from ..models.stock import Item, OrderLine
from ..models.user import User
from ..serializers.shift import ShiftSerializer


def check_credit(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            user = User.objects.filter(card=card)

            if not user:
                return HttpResponseRedirect(reverse_lazy('littleadmin:check'))

            return render(request, 'pos/credit_check.djhtml', {
                'form': CheckCreditForm(),
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


@login_required
def credit_overview(request):
    bought = OrderLine.objects.all().exclude(order__user__isnull=True).values('order__user').annotate(used=Sum('price'))
    users = User.objects.all().values()
    print(bought)
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
    crew = User.objects.all()

    credit_result = []
    for c in crew:
        items = OrderLine.objects.filter(order__user=c).values('item__name')\
            .annotate(total=Sum('price'), number=Sum(Case(When(price__gt=0, then=1), default=-1, output_field=IntegerField())))

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
        .annotate(total=Sum('price'), sold=Sum(Case(When(price__gt=0, then=1), default=-1, output_field=IntegerField())))

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
    print(shifts.data)
    return render(request, 'pos/sale_overview.djhtml', {'overview': overview, 'shifts': shifts.data, 'total': total})


@permission_required("user.update_credit")
def scan_user_card(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            user = User.objects.filter(card=card)

            if not user:
                return redirect('littleadmin:add_user', card=card)

            return redirect('littleadmin:edit_user_credit', card=card)
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:scan_user_card'))
    else:
        return render(request, 'pos/credit_check.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


@permission_required('user.update_credit')
def edit_user_credit(request, card=None):
    if request.POST:
        form = ChangeCreditForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data['credit']
            user = get_object_or_404(User, card=card)

            if user.is_crew:
                return HttpResponseBadRequest(b'Not allowed to update crew credit')

            user.credit = credit
            user.save()
            return redirect('littleadmin:scan_user_card')
    else:
        user = get_object_or_404(User, card=card)
        form = ChangeCreditForm(instance=user)

        return render(request, 'pos/credit_edit.djhtml', {'form': form, 'target': user})


@permission_required('user.create_user')
def add_user(request, card=None):
    if request.POST:
        form = AddUserForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']
            credit = form.cleaned_data['credit']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']

            user = User.create(card, credit, first_name, last_name, phone, email)

            user.save()

            return redirect('littleadmin:scan_user_card')
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:add_user'))
    else:
        form = AddUserForm(initial={'card': card})
        print(form['card'].value())
        return render(request, 'pos/add_user.djhtml', {
            'form': form
        })







