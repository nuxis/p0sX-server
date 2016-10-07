from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Sum, When
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from ..forms import ChangeCreditForm, CheckCreditForm
from ..models.crew import Crew
from ..models.shift import Shift
from ..models.stock import Item, OrderLine
from ..serializers.shift import ShiftSerializer


def check_credit(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            crew = Crew.objects.filter(card=card)

            if not crew:
                return HttpResponseRedirect(reverse_lazy('littleadmin:check'))

            return render(request, 'pos/credit_check.djhtml', {
                'form': CheckCreditForm(),
                'table': True,
                'used': crew[0].used,
                'credit': crew[0].credit,
                'left': crew[0].left
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
    bought = OrderLine.objects.all().exclude(order__crew__isnull=True).values('order__crew').annotate(used=Sum('price'))
    crew_list = Crew.objects.all().values()

    for crew in crew_list:
        for b in bought:
            crew['used'] = 0
            crew['left'] = 0
            if b['order__crew'] == crew['card']:
                crew['used'] = b['used']
                crew['left'] = crew['credit'] - crew['used']
                break

    context = {
        'crew_list': crew_list
    }

    return render(request, 'pos/credit_overview.djhtml', context)


@login_required
def credit_edit(request, card=None):
    if request.POST:
        form = ChangeCreditForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data['credit']
            crew = get_object_or_404(Crew, card=card)

            crew.credit = credit
            crew.save()
            return HttpResponseRedirect(reverse_lazy('littleadmin:overview'))
    else:
        crew = get_object_or_404(Crew, card=card)
        form = ChangeCreditForm(instance=crew)

        return render(request, 'pos/credit_edit.djhtml', {'form': form, 'crew': crew})


@login_required
def sale_overview(request):
    order_lines = OrderLine.objects.all().values('item__id', 'order__payment_method')\
        .annotate(total=Sum('price'), sold=Sum(Case(When(price__gt=1, then=1), default=-1, output_field=IntegerField())))

    items = Item.objects.all().values('name', 'category__name', 'id', 'price')
    total = {'cash': 0, 'crew': 0, 'total': 0}
    for item in items:
        per_payment_method = order_lines.filter(item_id=item['id'])
        try:
            crew = per_payment_method.filter(order__payment_method=1)[0]
        except IndexError:
            crew = {'sold': 0, 'total': 0}
        try:
            cash = per_payment_method.filter(order__payment_method=0)[0]
        except IndexError:
            cash = {'sold': 0, 'total': 0}
        item['cash'] = cash['total']
        item['crew'] = crew['total']
        item['sold'] = cash['sold'] + crew['sold']
        item['total'] = item['cash'] + item['crew']

        if item['price'] < 0:
            item['sold'] *= -1

        total['cash'] += item['cash']
        total['crew'] += item['crew']
        total['total'] += item['total']

    shifts = ShiftSerializer(Shift.objects.all(), many=True)

    return render(request, 'pos/sale_overview.djhtml', {'items': items, 'shifts': shifts.data, 'total': total})
